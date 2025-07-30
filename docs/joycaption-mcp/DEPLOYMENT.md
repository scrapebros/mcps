# JoyCaption MCP Server - Deployment Guide

## Overview

The JoyCaption MCP server has been successfully created and tested. Due to the model requirements (newer transformers version), the actual model couldn't be loaded in this environment, but the server structure and API are fully implemented.

## What's Included

### Core Files
- `joycaption_mcp/server.py` - Main MCP server implementation
- `mcp.json` - MCP configuration for Claude Code
- `requirements.txt` & `pyproject.toml` - Dependencies
- `README.md` - User documentation

### Testing & Examples
- `test_joycaption.py` - Direct model testing script
- `test_mcp_mock.py` - Mock test demonstrating functionality
- `example_client.py` - Usage examples
- `create_sample_images.py` - Generate test images
- `samples/` - 5 test images

## Deployment Steps

### 1. Environment Setup

```bash
# Clone or copy the joycaption-mcp directory
cd joycaption-mcp

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with updated dependencies
pip install --upgrade pip
pip install "transformers>=4.45.0" torch torchvision accelerate Pillow
pip install mcp>=0.9.0
pip install -e .
```

### 2. Model Requirements

**IMPORTANT**: The JoyCaption model requires:
- Transformers 4.45.0 or newer (for proper Llama 3.1 rope_scaling support)
- ~15GB disk space for model download
- 17GB+ VRAM for GPU mode (24GB recommended)
- CUDA-capable GPU (highly recommended for performance)

### 3. Configure Claude Code

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "joycaption": {
      "command": "python",
      "args": ["-m", "joycaption_mcp"],
      "env": {
        "CUDA_VISIBLE_DEVICES": "0"  // Optional: specify GPU
      }
    }
  }
}
```

### 4. First Run

The first time you use the `caption_image` tool, it will:
1. Download the model (~15GB)
2. Load it into memory
3. Cache it for future use

This may take 5-10 minutes depending on your internet speed.

## Usage Examples

### Basic Caption
```
caption_image {
  "image_path": "/path/to/image.jpg"
}
```

### With Options
```
caption_image {
  "image_path": "/path/to/image.jpg",
  "mode": "stable_diffusion",
  "create_json": true,
  "extra_options": ["lighting", "composition"],
  "temperature": 0.7
}
```

### Batch Processing
For multiple images, you can write a simple script:

```python
import os
from pathlib import Path

image_dir = Path("my_images")
for img in image_dir.glob("*.jpg"):
    # Use MCP client to call caption_image
    # with create_json=true for each image
```

## Troubleshooting

### Model Loading Issues
If you encounter rope_scaling errors:
```bash
pip install "transformers>=4.45.0" --upgrade
```

### Out of Memory
- Reduce max_tokens parameter
- Use CPU mode (slower): Set device_map="cpu" in server.py
- Consider quantization (not implemented yet)

### Performance
- GPU mode is 10-50x faster than CPU
- First caption is slow (model loading)
- Subsequent captions are faster (model cached)

## Future Enhancements

Possible improvements:
1. Model quantization support (8-bit, 4-bit)
2. Batch processing endpoint
3. Model caching between sessions
4. Progress indicators for long operations
5. Additional caption modes
6. Fine-tuning support

## Support

For issues:
1. Check transformers version: `pip show transformers`
2. Verify CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
3. Check available VRAM: `nvidia-smi`
4. Review server logs for errors

The mock test (`test_mcp_mock.py`) can help verify the server structure is working correctly without loading the actual model.