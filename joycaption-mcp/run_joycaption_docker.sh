#!/bin/bash

echo "JoyCaption MCP - Docker Runner"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Build the Docker image
echo "Building Docker image with JoyCaption dependencies..."
docker build -t joycaption-mcp:latest .

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "Docker build failed!"
    exit 1
fi

echo ""
echo "Docker image built successfully!"
echo ""

# Function to run JoyCaption on an image
run_caption() {
    local image_path=$1
    local mode=${2:-descriptive}
    
    echo "Running JoyCaption on: $image_path"
    echo "Mode: $mode"
    
    docker run --gpus all --rm \
        -v "$(pwd)":/workspace \
        -v "$HOME/.cache/huggingface":/app/.cache \
        joycaption-mcp:latest \
        python /workspace/test_joycaption_docker.py "/workspace/$image_path" "$mode"
}

# Main menu
echo "Options:"
echo "1. Test on a single image"
echo "2. Test on all images in samples/"
echo "3. Run MCP server"
echo "4. Interactive shell"
echo ""
read -p "Select option (1-4): " option

case $option in
    1)
        read -p "Enter image path: " img_path
        read -p "Enter mode (descriptive/straightforward/stable_diffusion/detailed_uncensored): " mode
        run_caption "$img_path" "$mode"
        ;;
    2)
        echo "Testing all images in samples/ directory..."
        for img in samples/*.png samples/*.jpg samples/*.jpeg; do
            if [ -f "$img" ]; then
                echo ""
                run_caption "$img" "detailed_uncensored"
                echo "Press Enter to continue..."
                read
            fi
        done
        ;;
    3)
        echo "Starting JoyCaption MCP server..."
        docker run --gpus all --rm -it \
            -v "$(pwd)":/workspace \
            -v "$HOME/.cache/huggingface":/app/.cache \
            -p 8080:8080 \
            joycaption-mcp:latest
        ;;
    4)
        echo "Starting interactive shell..."
        docker run --gpus all --rm -it \
            -v "$(pwd)":/workspace \
            -v "$HOME/.cache/huggingface":/app/.cache \
            joycaption-mcp:latest \
            /bin/bash
        ;;
    *)
        echo "Invalid option!"
        exit 1
        ;;
esac