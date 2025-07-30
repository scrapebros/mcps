#!/usr/bin/env python3
"""
Batch caption generator for JoyCaption
Processes a directory and creates captions only for images without existing JSON files
"""

import os
import sys
import json
from pathlib import Path
from PIL import Image
import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration
from tqdm import tqdm
import argparse
import time

# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'}

class JoyCaptionBatch:
    def __init__(self, model_name="fancyfeast/llama-joycaption-beta-one-hf-llava"):
        self.model_name = model_name
        self.model = None
        self.processor = None
        self.device = None
        
    def load_model(self):
        """Load JoyCaption model once for batch processing"""
        if self.model is not None:
            return
            
        print(f"Loading JoyCaption model: {self.model_name}")
        print("This may take a while on first run...")
        
        self.processor = AutoProcessor.from_pretrained(self.model_name)
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        if self.device == "cuda":
            self.model = LlavaForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
        else:
            self.model = LlavaForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                device_map="cpu"
            )
        
        self.model.eval()
        print("✓ Model loaded successfully!")
        
    def generate_caption(self, image_path, mode="descriptive"):
        """Generate caption for a single image"""
        # Load image
        image = Image.open(image_path).convert("RGB")
        
        # Caption prompts
        prompts = {
            "descriptive": "Write a long detailed description for this image.",
            "detailed_uncensored": "Describe this image in great detail. Include all visible elements, people, their appearance, clothing or lack thereof, poses, expressions, and any other relevant details. Be precise and comprehensive.",
            "straightforward": "Write a straightforward caption for this image. Begin with the main subject and medium. Mention pivotal elements—people, objects, scenery—using confident, definite language.",
            "stable_diffusion": "Output a stable diffusion prompt that is indistinguishable from a real stable diffusion prompt.",
            "training": "Write a detailed caption suitable for training a diffusion model. Include all visual elements, style, composition, and details."
        }
        
        prompt = prompts.get(mode, prompts["descriptive"])
        
        # Build conversation
        conversation = [
            {
                "role": "system",
                "content": "You are a helpful image captioner.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]
        
        # Format conversation
        convo_string = self.processor.apply_chat_template(
            conversation,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Process inputs
        inputs = self.processor(
            text=[convo_string],
            images=[image],
            return_tensors="pt"
        ).to(self.device)
        
        if self.device == "cuda":
            inputs['pixel_values'] = inputs['pixel_values'].to(torch.bfloat16)
        
        # Generate
        with torch.no_grad():
            generate_ids = self.model.generate(
                **inputs,
                max_new_tokens=512,
                do_sample=True,
                suppress_tokens=None,
                use_cache=True,
                temperature=0.6,
                top_k=None,
                top_p=0.9,
            )[0]
        
        # Decode
        generate_ids = generate_ids[inputs['input_ids'].shape[1]:]
        caption = self.processor.tokenizer.decode(
            generate_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        ).strip()
        
        return caption

def find_images_without_captions(directory):
    """Find all images in directory that don't have corresponding JSON files"""
    directory = Path(directory)
    images_to_process = []
    
    # Find all image files
    for ext in IMAGE_EXTENSIONS:
        for img_path in directory.rglob(f"*{ext}"):
            # Check if corresponding JSON exists
            json_path = img_path.with_suffix('.json')
            if not json_path.exists():
                images_to_process.append(img_path)
                
    return sorted(images_to_process)

def main():
    parser = argparse.ArgumentParser(description="Batch generate captions for images using JoyCaption")
    parser.add_argument("directory", help="Directory containing images")
    parser.add_argument("--mode", default="training", 
                       choices=["descriptive", "detailed_uncensored", "straightforward", "stable_diffusion", "training"],
                       help="Caption mode (default: training)")
    parser.add_argument("--recursive", action="store_true", help="Process subdirectories recursively")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without actually doing it")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="Skip images that already have JSON files (default: True)")
    
    args = parser.parse_args()
    
    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist")
        sys.exit(1)
        
    print(f"Processing directory: {directory}")
    print(f"Mode: {args.mode}")
    print(f"Recursive: {args.recursive}")
    print(f"Skip existing: {args.skip_existing}")
    print()
    
    # Find images to process
    if args.skip_existing:
        images = find_images_without_captions(directory)
        print(f"Found {len(images)} images without captions")
    else:
        images = []
        for ext in IMAGE_EXTENSIONS:
            pattern = f"**/*{ext}" if args.recursive else f"*{ext}"
            images.extend(directory.glob(pattern))
        images = sorted(images)
        print(f"Found {len(images)} total images")
    
    if not images:
        print("No images to process!")
        return
        
    # Dry run - just show what would be processed
    if args.dry_run:
        print("\nDry run - would process:")
        for img in images:
            print(f"  {img}")
        print(f"\nTotal: {len(images)} images")
        return
    
    # Load model
    captioner = JoyCaptionBatch()
    captioner.load_model()
    
    # Process images
    print(f"\nProcessing {len(images)} images...")
    successful = 0
    failed = 0
    
    with tqdm(images, desc="Generating captions") as pbar:
        for img_path in pbar:
            pbar.set_description(f"Processing {img_path.name}")
            
            try:
                # Generate caption
                start_time = time.time()
                caption = captioner.generate_caption(img_path, mode=args.mode)
                elapsed = time.time() - start_time
                
                # Save to JSON
                json_path = img_path.with_suffix('.json')
                caption_data = {
                    "caption": caption,
                    "model": captioner.model_name,
                    "mode": args.mode,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "processing_time": f"{elapsed:.2f}s"
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(caption_data, f, indent=2, ensure_ascii=False)
                
                successful += 1
                pbar.set_postfix({"success": successful, "failed": failed})
                
            except Exception as e:
                print(f"\n✗ Error processing {img_path}: {e}")
                failed += 1
                pbar.set_postfix({"success": successful, "failed": failed})
    
    # Summary
    print(f"\n{'='*60}")
    print("Batch processing complete!")
    print(f"✓ Successfully processed: {successful} images")
    if failed > 0:
        print(f"✗ Failed: {failed} images")
    print(f"Total time: {time.strftime('%H:%M:%S', time.gmtime(time.time()))}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()