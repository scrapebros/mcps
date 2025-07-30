#!/bin/bash

echo "JoyCaption MCP - Environment Fix Script"
echo "======================================"

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Running as root, good!"
else
   echo "Warning: Not running as root. Some fixes may not work."
fi

echo ""
echo "1. Checking Python version..."
python3 --version

echo ""
echo "2. Fixing cffi backend issue..."
# The cffi issue is often due to missing system libraries
apt-get update
apt-get install -y python3-cffi-backend libffi-dev

echo ""
echo "3. Reinstalling critical packages..."
pip3 install --upgrade --force-reinstall cffi
pip3 install --upgrade --force-reinstall cryptography

echo ""
echo "4. Testing imports..."
python3 -c "import cffi; print('✓ cffi OK')"
python3 -c "import cryptography; print('✓ cryptography OK')"

echo ""
echo "5. Creating clean virtual environment (recommended)..."
echo "Run these commands:"
echo "  cd /opt/mcps/joycaption-mcp"
echo "  python3 -m venv venv_clean"
echo "  source venv_clean/bin/activate"
echo "  pip install torch torchvision transformers pillow accelerate"
echo "  python test_server.py samples/"

echo ""
echo "6. Alternative: Use Docker (most reliable)..."
echo "Run:"
echo "  docker run --gpus all -it -v /opt/mcps/joycaption-mcp:/workspace pytorch/pytorch:latest bash"
echo "  # Inside container:"
echo "  cd /workspace"
echo "  pip install transformers pillow"
echo "  python test_server.py samples/"

echo ""
echo "Environment fix script complete!"