# JoyCaption MCP Server

An MCP (Model Context Protocol) server that provides image captioning capabilities using vision-language models. While originally designed for JoyCaption, it currently uses BLIP models due to compatibility with the current environment.

## Features

- Generate various types of captions for images (descriptive, straightforward, art critic, etc.)
- Support for 9 different caption modes
- Optional JSON file generation with caption metadata
- Customizable generation parameters (temperature, top_p, max tokens)
- Extra options to fine-tune caption output
- Works with Claude Code and other MCP-compatible applications
- Automatically selects best available model (BLIP-2, BLIP, or GIT)

## Installation

### Prerequisites

- Python 3.8 or higher
- CUDA-capable GPU (recommended) or CPU
- At least 4GB VRAM for GPU mode (8GB+ recommended for larger models)

### Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd joycaption-mcp
```

2. Install dependencies:
```bash
pip install -e .
```

3. The vision-language model will be downloaded automatically on first use (1-5GB depending on model).

## Configuration

### For Claude Code

Add the following to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "joycaption": {
      "command": "python",
      "args": ["-m", "joycaption_mcp"],
      "env": {}
    }
  }
}
```

### For other MCP clients

Use the command: `python -m joycaption_mcp`

## Usage

The server provides three main tools:

### 1. `caption_image`

Generate a caption for an image.

**Parameters:**
- `image_path` (required): Path to the image file
- `mode`: Caption mode (default: "descriptive")
  - `descriptive`: Detailed description
  - `descriptive_casual`: Casual tone description
  - `straightforward`: Concise, objective caption
  - `stable_diffusion`: Stable Diffusion style prompt
  - `midjourney`: MidJourney style prompt
  - `danbooru`: Tag-style listing
  - `art_critic`: Art critique analysis
  - `product_listing`: Product description
  - `social_media`: Social media caption
- `create_json`: Whether to save caption to JSON file (default: false)
- `word_count`: Optional word limit
- `length`: Optional length specification ("short", "medium", "long")
- `extra_options`: Array of extra options to add to prompt
- `temperature`: Generation temperature 0.1-1.0 (default: 0.6)
- `top_p`: Top-p sampling 0.1-1.0 (default: 0.9)
- `max_tokens`: Max tokens to generate 50-2048 (default: 512)

**Example:**
```
caption_image {
  "image_path": "/path/to/image.jpg",
  "mode": "descriptive",
  "create_json": true,
  "extra_options": ["lighting", "camera_angle"]
}
```

### 2. `list_caption_modes`

List all available caption modes and their descriptions.

### 3. `list_extra_options`

List all available extra options that can be added to prompts.

## Extra Options

You can customize caption output with these options:
- `lighting`: Include details about the lighting
- `camera_angle`: Mention the camera angle or perspective
- `composition`: Discuss the composition
- `aesthetic_quality`: Comment on the aesthetic quality
- `no_ambiguity`: Be precise and avoid ambiguous language
- `important_only`: Focus only on the most important elements

## JSON Output Format

When `create_json` is enabled, the caption is saved in this format:

```json
{
  "caption": "Generated caption text...",
  "mode": "descriptive",
  "extra_options": ["lighting", "camera_angle"],
  "temperature": 0.6,
  "top_p": 0.9,
  "model": "blip",
  "prompt": "Describe this image in detail:"
}
```

## System Requirements

- **GPU Mode**: 4GB+ VRAM (8GB recommended for BLIP-2)
- **CPU Mode**: Slower but works without GPU
- **Disk Space**: 1-5GB for model download

## Troubleshooting

1. **Out of Memory**: Try reducing `max_tokens` or use CPU mode
2. **Slow Generation**: GPU mode is highly recommended for reasonable speeds
3. **Model Download**: First run will download model files (1-5GB)

## License

This MCP server is provided as-is. JoyCaption model has its own license terms.

## Credits

Currently uses [BLIP](https://github.com/salesforce/BLIP) models by Salesforce. Designed to support [JoyCaption](https://huggingface.co/fancyfeast/llama-joycaption-beta-one-hf-llava) when compatible with environment.