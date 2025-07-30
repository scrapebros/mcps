import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

import torch
from PIL import Image

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caption modes and their prompts
CAPTION_MODES = {
    "descriptive": "Describe this image in detail:",
    "descriptive_casual": "Describe this image in a casual, conversational tone:",
    "straightforward": "What is in this image? Be concise and factual:",
    "stable_diffusion": "Create a detailed prompt for Stable Diffusion to recreate this image:",
    "midjourney": "Create a MidJourney prompt for this image:",
    "danbooru": "List the key elements of this image as tags:",
    "art_critic": "Analyze this image like an art critic, discussing composition, style, and meaning:",
    "product_listing": "Describe this image as if it were a product listing:",
    "social_media": "Write a social media caption for this image:"
}

# Extra options that can be appended to prompts
EXTRA_OPTIONS = {
    "lighting": " Include details about the lighting.",
    "camera_angle": " Mention the camera angle or perspective.",
    "composition": " Discuss the composition.",
    "aesthetic_quality": " Comment on the aesthetic quality.",
    "no_ambiguity": " Be precise and avoid ambiguous language.",
    "important_only": " Focus only on the most important elements."
}

class JoyCaptionServer:
    def __init__(self):
        self.server = Server("joycaption-mcp")
        self.model = None
        self.processor = None
        self.device = None
        self.model_type = None
        
        # Register handlers
        self.setup_handlers()
        
    def setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            return [
                types.Tool(
                    name="caption_image",
                    description="Generate a caption for an image using a vision-language model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image_path": {
                                "type": "string",
                                "description": "Path to the image file"
                            },
                            "mode": {
                                "type": "string",
                                "description": f"Caption mode. Options: {', '.join(CAPTION_MODES.keys())}",
                                "enum": list(CAPTION_MODES.keys()),
                                "default": "descriptive"
                            },
                            "create_json": {
                                "type": "boolean",
                                "description": "Whether to create a JSON caption file with the same name as the image",
                                "default": False
                            },
                            "extra_options": {
                                "type": "array",
                                "description": f"Extra options to append to the prompt. Available: {', '.join(EXTRA_OPTIONS.keys())}",
                                "items": {
                                    "type": "string",
                                    "enum": list(EXTRA_OPTIONS.keys())
                                }
                            },
                            "temperature": {
                                "type": "number",
                                "description": "Generation temperature (0.1-1.0)",
                                "default": 0.7,
                                "minimum": 0.1,
                                "maximum": 1.0
                            },
                            "top_p": {
                                "type": "number",
                                "description": "Top-p sampling parameter",
                                "default": 0.9,
                                "minimum": 0.1,
                                "maximum": 1.0
                            },
                            "max_tokens": {
                                "type": "integer",
                                "description": "Maximum number of tokens to generate",
                                "default": 256,
                                "minimum": 50,
                                "maximum": 1024
                            }
                        },
                        "required": ["image_path"]
                    }
                ),
                types.Tool(
                    name="list_caption_modes",
                    description="List all available caption modes and their descriptions",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="list_extra_options",
                    description="List all available extra options that can be added to prompts",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Optional[Dict[str, Any]]
        ) -> List[types.TextContent]:
            if name == "caption_image":
                return await self.caption_image(arguments)
            elif name == "list_caption_modes":
                return await self.list_caption_modes()
            elif name == "list_extra_options":
                return await self.list_extra_options()
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def ensure_model_loaded(self):
        """Load a vision-language model"""
        if self.model is None:
            logger.info("Loading vision-language model...")
            
            # Check for CUDA availability
            if torch.cuda.is_available():
                self.device = "cuda"
                device_map = "auto"
            else:
                self.device = "cpu"
                device_map = "cpu"
                logger.warning("CUDA not available, using CPU. This will be slower.")
            
            # Try different model options
            loaded = False
            
            # Option 1: Try BLIP-2 (most compatible)
            if not loaded:
                try:
                    from transformers import Blip2Processor, Blip2ForConditionalGeneration
                    
                    model_name = "Salesforce/blip2-opt-2.7b"
                    logger.info(f"Loading BLIP-2 model: {model_name}")
                    
                    self.processor = Blip2Processor.from_pretrained(model_name)
                    self.model = Blip2ForConditionalGeneration.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                        device_map=device_map
                    )
                    self.model_type = "blip2"
                    loaded = True
                    logger.info("✓ BLIP-2 model loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load BLIP-2: {e}")
            
            # Option 2: Try BLIP original
            if not loaded:
                try:
                    from transformers import BlipProcessor, BlipForConditionalGeneration
                    
                    model_name = "Salesforce/blip-image-captioning-large"
                    logger.info(f"Loading BLIP model: {model_name}")
                    
                    self.processor = BlipProcessor.from_pretrained(model_name)
                    self.model = BlipForConditionalGeneration.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                    ).to(self.device)
                    self.model_type = "blip"
                    loaded = True
                    logger.info("✓ BLIP model loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load BLIP: {e}")
            
            # Option 3: Try GIT
            if not loaded:
                try:
                    from transformers import AutoProcessor, AutoModelForCausalLM
                    
                    model_name = "microsoft/git-base"
                    logger.info(f"Loading GIT model: {model_name}")
                    
                    self.processor = AutoProcessor.from_pretrained(model_name)
                    self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)
                    self.model_type = "git"
                    loaded = True
                    logger.info("✓ GIT model loaded successfully")
                except Exception as e:
                    logger.warning(f"Failed to load GIT: {e}")
            
            if not loaded:
                raise RuntimeError("Could not load any vision-language model. Please install transformers and torch.")
            
            self.model.eval()
            logger.info(f"Model ready on {self.device}")
    
    async def caption_image(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Generate a caption for an image"""
        try:
            # Ensure model is loaded
            await self.ensure_model_loaded()
            
            # Extract arguments
            image_path = Path(arguments["image_path"])
            mode = arguments.get("mode", "descriptive")
            create_json = arguments.get("create_json", False)
            extra_options = arguments.get("extra_options", [])
            temperature = arguments.get("temperature", 0.7)
            top_p = arguments.get("top_p", 0.9)
            max_tokens = arguments.get("max_tokens", 256)
            
            # Validate image exists
            if not image_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"Error: Image file not found: {image_path}"
                )]
            
            # Load image
            try:
                image = Image.open(image_path).convert("RGB")
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error loading image: {str(e)}"
                )]
            
            # Build the prompt
            prompt = CAPTION_MODES.get(mode, CAPTION_MODES["descriptive"])
            
            # Add extra options
            for option in extra_options:
                if option in EXTRA_OPTIONS:
                    prompt += EXTRA_OPTIONS[option]
            
            # Generate caption based on model type
            caption = None
            
            if self.model_type == "blip2":
                inputs = self.processor(image, text=prompt, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        do_sample=True,
                        temperature=temperature,
                        top_p=top_p
                    )
                
                caption = self.processor.decode(outputs[0], skip_special_tokens=True).strip()
            
            elif self.model_type == "blip":
                # For original BLIP, we can use conditional or unconditional generation
                if mode == "straightforward":
                    # Unconditional generation
                    inputs = self.processor(image, return_tensors="pt").to(self.device)
                else:
                    # Conditional generation with prompt
                    inputs = self.processor(image, text=prompt, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_length=max_tokens,
                        num_beams=3,
                        temperature=temperature,
                        top_p=top_p
                    )
                
                caption = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            elif self.model_type == "git":
                inputs = self.processor(images=image, return_tensors="pt").to(self.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        pixel_values=inputs.pixel_values,
                        max_length=max_tokens,
                        do_sample=True,
                        temperature=temperature,
                        top_p=top_p
                    )
                
                caption = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
            
            # Clean up caption
            if caption and prompt in caption:
                caption = caption.replace(prompt, "").strip()
            
            # Create JSON file if requested
            if create_json:
                json_path = image_path.with_suffix('.json')
                caption_data = {
                    "caption": caption,
                    "mode": mode,
                    "extra_options": extra_options,
                    "temperature": temperature,
                    "top_p": top_p,
                    "model": self.model_type,
                    "prompt": prompt
                }
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(caption_data, f, indent=2, ensure_ascii=False)
                
                return [types.TextContent(
                    type="text",
                    text=f"Caption: {caption}\n\nJSON file created at: {json_path}"
                )]
            
            return [types.TextContent(
                type="text",
                text=caption
            )]
            
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}", exc_info=True)
            return [types.TextContent(
                type="text",
                text=f"Error generating caption: {str(e)}"
            )]
    
    async def list_caption_modes(self) -> List[types.TextContent]:
        """List all available caption modes"""
        modes_text = "Available caption modes:\n\n"
        for mode, prompt in CAPTION_MODES.items():
            modes_text += f"**{mode}**: {prompt}\n\n"
        
        return [types.TextContent(type="text", text=modes_text)]
    
    async def list_extra_options(self) -> List[types.TextContent]:
        """List all available extra options"""
        options_text = "Available extra options:\n\n"
        for option, description in EXTRA_OPTIONS.items():
            options_text += f"**{option}**: {description.strip()}\n\n"
        
        return [types.TextContent(type="text", text=options_text)]
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="JoyCaption MCP",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

def main():
    """Main entry point"""
    server = JoyCaptionServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()