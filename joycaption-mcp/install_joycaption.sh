#!/bin/bash

echo "JoyCaption Direct Installation Script"
echo "===================================="
echo ""
echo "This script will install JoyCaption with the required dependencies."
echo "Note: Requires Python 3.8+ and CUDA-capable GPU"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv joycaption_env

# Activate it
source joycaption_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install PyTorch first (adjust CUDA version as needed)
echo "Installing PyTorch..."
pip install torch==2.1.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install specific transformers version for JoyCaption
echo "Installing transformers 4.45.2 for JoyCaption..."
pip install transformers==4.45.2

# Install other dependencies
echo "Installing other dependencies..."
pip install accelerate Pillow sentencepiece protobuf einops scipy mcp

# Test import
echo ""
echo "Testing installation..."
python -c "
import torch
import transformers
print(f'PyTorch: {torch.__version__}')
print(f'Transformers: {transformers.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print('✓ Installation successful!')
"

echo ""
echo "To use JoyCaption, activate the environment with:"
echo "  source joycaption_env/bin/activate"
echo ""
echo "Then run:"
echo "  python test_joycaption_docker.py <image_path>"
echo ""
echo "For the MCP server:"
echo "  python -m joycaption_mcp"