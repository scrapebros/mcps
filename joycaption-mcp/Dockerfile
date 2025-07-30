FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements_joycaption.txt /app/

# Install Python dependencies with specific versions for JoyCaption
RUN pip install --no-cache-dir \
    transformers==4.45.2 \
    torch==2.1.0 \
    torchvision \
    accelerate \
    Pillow \
    sentencepiece \
    protobuf \
    mcp

# Copy the application
COPY . /app/

# Set environment variables
ENV CUDA_VISIBLE_DEVICES=0
ENV TRANSFORMERS_CACHE=/app/.cache
ENV HF_HOME=/app/.cache

# Create cache directory
RUN mkdir -p /app/.cache

# Entry point
CMD ["python", "-m", "joycaption_mcp"]