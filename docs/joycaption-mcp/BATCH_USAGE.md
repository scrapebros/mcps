# JoyCaption Batch Processing Guide

## Overview

The `batch_caption.py` script processes entire directories of images, automatically creating JSON caption files for training datasets. It only processes images that don't already have captions, making it safe to run repeatedly.

## Features

- ✅ Skips images that already have JSON caption files
- ✅ Supports recursive directory processing
- ✅ Progress bar with time estimates
- ✅ Multiple caption modes for different use cases
- ✅ Dry-run mode to preview what will be processed
- ✅ Handles errors gracefully, continues with remaining images

## Installation

```bash
# Use the virtual environment with JoyCaption
source joycaption_env/bin/activate

# Or create new environment
python3 -m venv joycaption_env
source joycaption_env/bin/activate
pip install torch torchvision transformers==4.45.2 Pillow tqdm
```

## Basic Usage

```bash
# Process a directory (only missing captions)
python batch_caption.py /path/to/images/

# Process with specific mode
python batch_caption.py /path/to/images/ --mode detailed_uncensored

# Process recursively (all subdirectories)
python batch_caption.py /path/to/images/ --recursive

# Dry run (see what would be processed)
python batch_caption.py /path/to/images/ --dry-run
```

## Caption Modes

1. **training** (default) - Best for diffusion model training
2. **detailed_uncensored** - Most comprehensive descriptions
3. **descriptive** - General detailed descriptions
4. **straightforward** - Concise, factual captions
5. **stable_diffusion** - SD prompt style

## JSON Output Format

Each image gets a corresponding JSON file with the same name:
- `image1.png` → `image1.json`
- `photo.jpg` → `photo.json`

JSON contents:
```json
{
  "caption": "Detailed description of the image...",
  "model": "fancyfeast/llama-joycaption-beta-one-hf-llava",
  "mode": "training",
  "timestamp": "2025-07-28 17:02:18",
  "processing_time": "2.45s"
}
```

## Example Workflow

### For Training Dataset Preparation

```bash
# 1. Organize your images
mkdir -p dataset/train dataset/val

# 2. Run captioning on training set
python batch_caption.py dataset/train/ --mode training --recursive

# 3. Run on validation set
python batch_caption.py dataset/val/ --mode training --recursive

# 4. Verify all images have captions
python batch_caption.py dataset/ --recursive --dry-run
# Should show: "No images to process!"
```

### For Re-running After Adding New Images

```bash
# Add new images to dataset/
cp new_images/*.png dataset/train/

# Re-run batch script - only new images will be processed
python batch_caption.py dataset/ --recursive

# Check what was processed
ls -la dataset/train/*.json | tail -10
```

## Performance

- First image: ~1-2 minutes (model loading)
- Subsequent images: ~2-5 seconds each
- GPU recommended (17GB+ VRAM)
- Batch of 1000 images: ~1-2 hours

## Advanced Usage

### Process Multiple Directories

```bash
#!/bin/bash
for dir in dataset1 dataset2 dataset3; do
    echo "Processing $dir..."
    python batch_caption.py "$dir" --recursive --mode training
done
```

### Find Images Without Captions

```bash
# Find all PNG/JPG without JSON
find dataset/ -type f \( -name "*.png" -o -name "*.jpg" \) | while read img; do
    json="${img%.*}.json"
    [ ! -f "$json" ] && echo "Missing: $img"
done
```

### Parallel Processing (Multiple GPUs)

```bash
# GPU 0
CUDA_VISIBLE_DEVICES=0 python batch_caption.py dataset/part1/ &

# GPU 1
CUDA_VISIBLE_DEVICES=1 python batch_caption.py dataset/part2/ &

wait
```

## Docker Usage

For systems with dependency issues:

```bash
# Using the Docker setup
docker run --gpus all -v /path/to/images:/images joycaption-mcp:latest \
    python batch_caption.py /images --recursive --mode training
```

## Troubleshooting

1. **Out of Memory**: Reduce batch size or use CPU mode
2. **Slow Processing**: Ensure using GPU with CUDA
3. **Missing Captions**: Check file permissions
4. **Errors on Specific Images**: Script continues, check summary at end

## Integration with Training

After generating captions, use them in your training script:

```python
# Example: Loading captions for training
import json
from pathlib import Path

def load_caption(image_path):
    json_path = Path(image_path).with_suffix('.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data['caption']

# In your dataset class
caption = load_caption("image.png")
```

This batch processing system makes it easy to prepare large datasets for diffusion model training with accurate, uncensored captions.