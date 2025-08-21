#!/bin/bash

# Setup script for GUI environment and fake webcam
# This enables full GUI testing and webcam simulation

set -e

echo "🎥 Setting up GUI Environment and Fake Webcam for MCP Playwright"
echo "================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_color() {
    echo -e "${2}${1}${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   print_color "Please run this script with sudo, not as root" "$RED"
   exit 1
fi

# Update package list
print_color "📦 Updating package list..." "$GREEN"
sudo apt-get update

# Install Xvfb (X Virtual Framebuffer) for headless GUI
print_color "🖥️ Installing Xvfb for headless GUI..." "$GREEN"
sudo apt-get install -y xvfb x11vnc x11-utils x11-xserver-utils

# Install video and webcam tools
print_color "📹 Installing video and webcam tools..." "$GREEN"
sudo apt-get install -y \
    ffmpeg \
    v4l-utils \
    v4l2loopback-dkms \
    v4l2loopback-utils \
    imagemagick \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly

# Install GUI libraries
print_color "🎨 Installing GUI libraries..." "$GREEN"
sudo apt-get install -y \
    libgtk-3-0 \
    libgbm-dev \
    libnotify-dev \
    libnss3 \
    libxss1 \
    libasound2 \
    libxtst6 \
    xauth \
    xvfb \
    fonts-liberation \
    libappindicator3-1 \
    libu2f-udev \
    libvulkan1

# Install lightweight desktop environment (optional)
print_color "🖥️ Install lightweight desktop environment? (y/n)" "$YELLOW"
read -r install_desktop

if [ "$install_desktop" = "y" ]; then
    print_color "Installing XFCE4 (lightweight desktop)..." "$GREEN"
    sudo apt-get install -y xfce4 xfce4-terminal
    
    # Install VNC server for remote desktop access
    sudo apt-get install -y tightvncserver
fi

# Load v4l2loopback module for fake webcam
print_color "🎥 Setting up fake webcam module..." "$GREEN"
sudo modprobe v4l2loopback devices=2 video_nr=20,21 card_label="Fake Webcam,Secondary Cam" exclusive_caps=1,1 || true

# Make it persistent across reboots
echo "v4l2loopback" | sudo tee -a /etc/modules
echo "options v4l2loopback devices=2 video_nr=20,21 card_label=\"Fake Webcam,Secondary Cam\" exclusive_caps=1,1" | sudo tee /etc/modprobe.d/v4l2loopback.conf

# Create test images for fake webcam
print_color "🖼️ Creating test images for webcam..." "$GREEN"
mkdir -p /opt/mcp-playwright/webcam-assets

# Create a test pattern image
convert -size 640x480 xc:blue \
    -fill white -pointsize 48 \
    -draw "text 100,240 'MCP Playwright Webcam'" \
    /opt/mcp-playwright/webcam-assets/test-pattern.jpg

# Create a fake person image using ImageMagick
convert -size 640x480 xc:lightblue \
    -fill brown -draw "circle 320,200 320,120" \
    -fill peachpuff -draw "circle 320,200 320,140" \
    -fill black -draw "circle 290,180 290,170" \
    -fill black -draw "circle 350,180 350,170" \
    -fill red -draw "ellipse 320,230 30,15 0,360" \
    -fill white -pointsize 24 \
    -draw "text 220,350 'Test User'" \
    /opt/mcp-playwright/webcam-assets/fake-person.jpg

# Create animated GIF for webcam
convert -size 640x480 -delay 50 \
    xc:red xc:green xc:blue xc:yellow \
    -fill white -pointsize 36 \
    -draw "text 200,240 'Frame %[fx:t+1]'" \
    /opt/mcp-playwright/webcam-assets/animated.gif

# Create video file for streaming
ffmpeg -f lavfi -i testsrc=duration=10:size=640x480:rate=30 \
    -f lavfi -i sine=frequency=1000:duration=10 \
    -pix_fmt yuv420p \
    /opt/mcp-playwright/webcam-assets/test-video.mp4 -y

print_color "✅ GUI and Webcam setup complete!" "$GREEN"
echo ""
print_color "📋 Available Features:" "$YELLOW"
echo "  • Xvfb for headless GUI testing"
echo "  • Fake webcam devices at /dev/video20 and /dev/video21"
echo "  • Test images and videos in /opt/mcp-playwright/webcam-assets/"
echo "  • FFmpeg for video processing"
echo "  • V4L2 tools for webcam control"

if [ "$install_desktop" = "y" ]; then
    echo "  • XFCE4 desktop environment"
    echo "  • VNC server for remote access"
fi

echo ""
print_color "🚀 Quick Test Commands:" "$GREEN"
echo "  Start Xvfb:     Xvfb :99 -screen 0 1920x1080x24 &"
echo "  Export display: export DISPLAY=:99"
echo "  List cameras:   v4l2-ctl --list-devices"
echo "  Test webcam:    ffplay /dev/video20"
echo ""

# Create helper script for starting GUI environment
cat > /opt/mcp-playwright/scripts/start-gui.sh << 'EOF'
#!/bin/bash
# Start virtual display for GUI testing

# Kill any existing Xvfb
pkill Xvfb || true

# Start Xvfb on display :99
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &
export DISPLAY=:99

# Wait for X server to start
sleep 2

# Optional: Start window manager if installed
if command -v xfwm4 &> /dev/null; then
    xfwm4 --display=:99 &
fi

echo "Virtual display started on DISPLAY=:99"
echo "Set environment: export DISPLAY=:99"
EOF

chmod +x /opt/mcp-playwright/scripts/start-gui.sh

print_color "✨ Setup complete! Use ./scripts/start-gui.sh to start virtual display" "$GREEN"