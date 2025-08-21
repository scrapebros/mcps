# MCP Playwright Server with Webcam and GUI Support
FROM mcr.microsoft.com/playwright:v1.48.0-focal

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Build tools
    build-essential \
    curl \
    wget \
    git \
    # GUI and X11
    xvfb \
    x11vnc \
    x11-utils \
    x11-xserver-utils \
    # Video and webcam tools
    ffmpeg \
    v4l-utils \
    imagemagick \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    # GUI libraries
    libgtk-3-0 \
    libgbm-dev \
    libnotify-dev \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    xauth \
    fonts-liberation \
    libappindicator3-1 \
    libu2f-udev \
    libvulkan1 \
    # Python
    python3 \
    python3-pip \
    python3-venv \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install v4l2loopback from source (since we can't use DKMS in Docker)
RUN git clone https://github.com/umlaeute/v4l2loopback.git /tmp/v4l2loopback \
    && cd /tmp/v4l2loopback \
    && make \
    && make install \
    && depmod -a \
    && rm -rf /tmp/v4l2loopback

# Set working directory
WORKDIR /opt/mcp-playwright

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install Node dependencies
RUN npm ci

# Copy Python requirements
COPY requirements.txt ./

# Setup Python environment
RUN python3 -m venv venv \
    && . venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && playwright install

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p \
    /opt/mcp-playwright/webcam-assets \
    /opt/mcp-playwright/reports/screenshots \
    /opt/mcp-playwright/reports/test-results \
    /opt/mcp-playwright/reports/html

# Create test assets for webcam
RUN convert -size 640x480 xc:blue \
    -fill white -pointsize 48 \
    -draw "text 100,240 'MCP Playwright Webcam'" \
    /opt/mcp-playwright/webcam-assets/test-pattern.jpg \
    && convert -size 640x480 xc:lightblue \
    -fill brown -draw "circle 320,200 320,120" \
    -fill peachpuff -draw "circle 320,200 320,140" \
    -fill black -draw "circle 290,180 290,170" \
    -fill black -draw "circle 350,180 350,170" \
    -fill red -draw "ellipse 320,230 30,15 0,360" \
    -fill white -pointsize 24 \
    -draw "text 220,350 'Test User'" \
    /opt/mcp-playwright/webcam-assets/fake-person.jpg \
    && ffmpeg -f lavfi -i testsrc=duration=10:size=640x480:rate=30 \
    -pix_fmt yuv420p \
    /opt/mcp-playwright/webcam-assets/test-video.mp4 -y

# Build TypeScript
RUN npm run build

# Create startup script
RUN echo '#!/bin/bash\n\
# Start virtual display\n\
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &\n\
export DISPLAY=:99\n\
\n\
# Load v4l2loopback module (requires --privileged)\n\
modprobe v4l2loopback devices=2 video_nr=20,21 card_label="Fake Webcam,Secondary Cam" exclusive_caps=1,1 || true\n\
\n\
# Start MCP server\n\
exec node /opt/mcp-playwright/build/index.js\n\
' > /opt/mcp-playwright/start.sh \
    && chmod +x /opt/mcp-playwright/start.sh

# Set environment variables
ENV DISPLAY=:99
ENV NODE_ENV=production
ENV PYTHONPATH=/opt/mcp-playwright

# Expose port for optional debugging
EXPOSE 9229

# Entry point
CMD ["/opt/mcp-playwright/start.sh"]