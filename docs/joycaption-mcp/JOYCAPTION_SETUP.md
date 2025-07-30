# JoyCaption MCP - Using the Actual JoyCaption Model

## The Problem

The BLIP models included as fallbacks are censored and struggle with certain content, producing outputs like "frng fr frng" instead of accurate descriptions. This defeats the purpose of JoyCaption, which was designed to be uncensored and accurate for all types of content.

## The Solution

To use the actual JoyCaption model, you need:
- transformers >= 4.45.0 (for proper Llama 3.1 support)
- PyTorch 2.1.0+
- 17GB+ VRAM

## Installation Methods

### Method 1: Docker (Recommended)

```bash
cd /opt/mcps/joycaption-mcp

# Build and run with Docker
./run_joycaption_docker.sh

# Select option 2 to test all images
# Select option 3 to run the MCP server
```

### Method 2: Direct Installation

```bash
cd /opt/mcps/joycaption-mcp

# Run the installation script
./install_joycaption.sh

# Activate the environment
source joycaption_env/bin/activate

# Test on an image
python test_joycaption_docker.py samples/2025-07-27_21-37-15_4891.png detailed_uncensored
```

### Method 3: Manual Setup

```bash
# Create fresh environment
python3 -m venv joycaption_env
source joycaption_env/bin/activate

# Install dependencies
pip install torch==2.1.0 torchvision --index-url https://download.pytorch.org/whl/cu121
pip install transformers==4.45.2 accelerate Pillow sentencepiece protobuf einops scipy mcp

# Run the test
python test_joycaption_docker.py <image_path>
```

## Testing on Your Images

The script includes a special mode for uncensored content:

```bash
# For detailed, uncensored descriptions
python test_joycaption_docker.py samples/your_image.png detailed_uncensored
```

## Expected Results

With the actual JoyCaption model, you should get:
- Accurate descriptions of all visual elements
- No censorship or refusal to describe content
- Detailed information about people, appearances, clothing/lack thereof
- Professional, descriptive language without euphemisms

## Example Outputs

Instead of BLIP's censored output:
- ❌ "a woman with frng fr frng her eyes"

JoyCaption would provide:
- ✅ "A close-up photograph of a woman with long blonde hair partially covering her face..."

## MCP Server with JoyCaption

Once installed, update the server to use JoyCaption:

```python
# In joycaption_mcp/server.py, replace the model loading section with:
model_name = "fancyfeast/llama-joycaption-beta-one-hf-llava"
# ... rest of JoyCaption loading code
```

## Troubleshooting

1. **Out of Memory**: JoyCaption needs ~17GB VRAM. Use a smaller batch size or CPU mode (slow).

2. **Import Errors**: Ensure you're using the joycaption_env with transformers 4.45.2.

3. **Model Download**: First run downloads ~15GB. Ensure stable internet and disk space.

## Why This Matters

JoyCaption was specifically created to:
- Provide uncensored, accurate descriptions
- Support all types of content equally
- Enable training of diffusion models on diverse datasets
- Avoid the limitations of censored models like ChatGPT or BLIP

The censorship you encountered with BLIP is exactly what JoyCaption aims to solve.