# Webcam and GUI Environment Setup

Complete guide for setting up fake webcam devices and GUI environment for comprehensive web testing.

## Table of Contents

- [Overview](#overview)
- [GUI Environment](#gui-environment)
- [Webcam Simulation](#webcam-simulation)
- [MCP Webcam Tools](#mcp-webcam-tools)
- [Testing Examples](#testing-examples)
- [Troubleshooting](#troubleshooting)

## Overview

MCP Playwright includes powerful capabilities for:
- **Fake Webcam Devices**: Simulate webcam input for testing video applications
- **Virtual Display**: Run browsers with full GUI support in headless environments
- **Screen Capture**: Stream screen content to virtual webcam devices
- **Media Testing**: Test video conferencing, streaming, and camera-based applications

## GUI Environment

### Virtual Display Setup

The system uses Xvfb (X Virtual Framebuffer) for headless GUI operations:

```bash
# Start virtual display
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Or use the provided script
./scripts/start-gui.sh
```

### Ubuntu Desktop (Optional)

For full desktop environment:

```bash
# Install XFCE4 desktop
sudo apt-get install -y xfce4 xfce4-terminal

# Start desktop session
startxfce4 --display=:99 &

# Connect via VNC (if installed)
x11vnc -display :99 -forever -nopw
```

### GUI Libraries

Required libraries are installed via setup script:
- GTK3, GBM for rendering
- NSS3, ALSA for browser support
- X11 utilities for display management

## Webcam Simulation

### Virtual Webcam Devices

The system creates two virtual webcam devices:
- `/dev/video20` - Primary fake webcam
- `/dev/video21` - Secondary fake webcam

### Webcam Modes

1. **Image Mode**: Stream static images
   ```typescript
   await webcamManager.startWebcam({
     mode: 'image',
     source: '/path/to/image.jpg',
     loop: true
   });
   ```

2. **Video Mode**: Stream video files
   ```typescript
   await webcamManager.startWebcam({
     mode: 'video',
     source: '/path/to/video.mp4',
     loop: true
   });
   ```

3. **Pattern Mode**: Generate test patterns
   ```typescript
   await webcamManager.startWebcam({
     mode: 'pattern',
     source: 'smpte'  // or 'testsrc', 'testsrc2', 'rgbtestsrc'
   });
   ```

4. **Color Mode**: Solid color output
   ```typescript
   await webcamManager.startWebcam({
     mode: 'color',
     source: 'blue'  // Any valid color name
   });
   ```

5. **Screen Mode**: Capture display output
   ```typescript
   await webcamManager.startWebcam({
     mode: 'screen',
     source: ':99'  // Display number
   });
   ```

6. **Text Mode**: Display custom text
   ```typescript
   await webcamManager.startWebcam({
     mode: 'text',
     source: 'Hello World'
   });
   ```

## MCP Webcam Tools

### Available Tools

The MCP server provides these webcam control tools:

#### start_webcam
Start a fake webcam stream with various modes.

**Parameters:**
- `device`: Webcam device path (default: `/dev/video20`)
- `mode`: Stream mode (`image`, `video`, `pattern`, `color`, `screen`, `text`)
- `source`: Source content (file path, color, pattern type, or text)
- `loop`: Loop media playback (default: `true`)

**Example:**
```json
{
  "tool": "start_webcam",
  "arguments": {
    "mode": "pattern",
    "source": "smpte",
    "device": "/dev/video20"
  }
}
```

#### stop_webcam
Stop an active webcam stream.

**Parameters:**
- `device`: Device to stop (default: `/dev/video20`)

#### capture_webcam_photo
Capture a photo from the webcam.

**Parameters:**
- `device`: Device to capture from (default: `/dev/video20`)

**Returns:**
- Base64 encoded image
- File path to saved image

#### webcam_status
Get current webcam status.

**Parameters:**
- `device`: Device to check (default: `/dev/video20`)

**Returns:**
- Device existence status
- Streaming status
- Current mode

#### list_webcams
List all available webcam devices.

**Returns:**
- Array of available video devices

## Testing Examples

### JavaScript/TypeScript Testing

```typescript
import { test, expect } from '@playwright/test';
import { WebcamManager } from '../src/webcam-tools';

test('test video call with fake webcam', async ({ page, context }) => {
  const webcamManager = new WebcamManager();
  
  // Start fake webcam
  await webcamManager.startWebcam({
    mode: 'pattern',
    source: 'smpte'
  });
  
  // Grant camera permissions
  await context.grantPermissions(['camera']);
  
  // Navigate to video app
  await page.goto('https://your-video-app.com');
  
  // Camera will use fake webcam automatically
  await page.click('#start-video');
  
  // Verify video is working
  const videoActive = await page.locator('video').evaluate(
    video => !video.paused
  );
  expect(videoActive).toBe(true);
  
  // Cleanup
  webcamManager.stopWebcam();
});
```

### Python Testing

```python
from playwright.sync_api import sync_playwright
from scripts.webcam_controller import WebcamController

def test_video_conference():
    webcam = WebcamController()
    
    # Start fake webcam with test pattern
    webcam.stream_test_pattern("smpte")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            permissions=["camera", "microphone"]
        )
        page = context.new_page()
        
        # Test video application
        page.goto("https://your-app.com")
        page.click("#join-call")
        
        # Verify webcam is active
        assert page.locator("video").is_visible()
        
        browser.close()
    
    webcam.stop_stream()
```

### Command Line Usage

```bash
# Start webcam with test pattern
python scripts/webcam-controller.py pattern --source smpte

# Stream an image
python scripts/webcam-controller.py image --source /path/to/image.jpg

# Stream screen capture
python scripts/webcam-controller.py screen --display :99

# Capture photo from webcam
python scripts/webcam-controller.py capture

# Check webcam status
python scripts/webcam-controller.py status
```

## Use Cases

### 1. Video Conferencing Testing

Test video call applications with controlled input:

```typescript
// Test with different lighting conditions
await webcamManager.startWebcam({ mode: 'color', source: 'black' }); // Dark
await webcamManager.startWebcam({ mode: 'color', source: 'white' }); // Bright

// Test with motion
await webcamManager.startWebcam({ 
  mode: 'video', 
  source: 'test-motion.mp4' 
});
```

### 2. QR Code Scanning

Test QR code readers:

```typescript
// Display QR code image
await webcamManager.startWebcam({
  mode: 'image',
  source: 'qr-code.png',
  loop: false
});

// Test scanner
await page.click('#scan-qr');
const result = await page.textContent('#scan-result');
expect(result).toBe('Expected QR content');
```

### 3. Face Detection Testing

Test face detection features:

```typescript
// Use prepared face image
await webcamManager.startWebcam({
  mode: 'image',
  source: '/opt/mcp-playwright/webcam-assets/fake-person.jpg'
});

// Test detection
await page.click('#detect-face');
const detected = await page.locator('.face-detected').isVisible();
expect(detected).toBe(true);
```

### 4. Multi-Camera Testing

Test applications that use multiple cameras:

```typescript
// Start multiple cameras
await webcamManager.startWebcam({
  device: '/dev/video20',
  mode: 'pattern',
  source: 'smpte'
});

await webcamManager.startWebcam({
  device: '/dev/video21',
  mode: 'color',
  source: 'green'
});

// Application can now access both cameras
```

## Troubleshooting

### Common Issues

#### Webcam Device Not Found

```bash
# Check if v4l2loopback module is loaded
lsmod | grep v4l2loopback

# Load module if missing
sudo modprobe v4l2loopback devices=2 video_nr=20,21

# Verify devices exist
ls -la /dev/video*
```

#### FFmpeg Errors

```bash
# Check FFmpeg installation
ffmpeg -version

# Install if missing
sudo apt-get install -y ffmpeg

# Test with simple command
ffmpeg -f lavfi -i testsrc -t 1 -f null -
```

#### Permission Issues

```bash
# Add user to video group
sudo usermod -a -G video $USER

# Set device permissions
sudo chmod 666 /dev/video20 /dev/video21

# Restart session for group changes
```

#### Display Not Found

```bash
# Check if Xvfb is running
ps aux | grep Xvfb

# Start if not running
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Verify display
xdpyinfo -display :99
```

### Debug Commands

```bash
# List video devices
v4l2-ctl --list-devices

# Check device capabilities
v4l2-ctl -d /dev/video20 --all

# Test webcam output
ffplay /dev/video20

# Monitor FFmpeg processes
ps aux | grep ffmpeg

# Check X display
echo $DISPLAY
xwininfo -root -display :99
```

### Performance Tips

1. **Use appropriate resolution**:
   ```typescript
   // Lower resolution for faster processing
   await page.setViewportSize({ width: 1280, height: 720 });
   ```

2. **Optimize stream settings**:
   ```bash
   # Reduce frame rate for less CPU usage
   ffmpeg -r 15 ...  # 15 fps instead of 30
   ```

3. **Clean up resources**:
   ```typescript
   // Always stop webcams after tests
   afterEach(async () => {
     await webcamManager.cleanup();
   });
   ```

## Advanced Configuration

### Custom FFmpeg Parameters

Modify `webcam-tools.ts` for custom streaming:

```typescript
// Add custom FFmpeg filters
command.push('-vf', 'scale=640:480,format=yuv420p');

// Adjust quality
command.push('-b:v', '1M');  // Bitrate
command.push('-preset', 'ultrafast');  // Encoding speed
```

### Multiple Display Support

```bash
# Start multiple displays
Xvfb :99 -screen 0 1920x1080x24 &
Xvfb :100 -screen 0 1280x720x24 &

# Use different displays for different tests
export DISPLAY=:99  # Main tests
export DISPLAY=:100  # Secondary tests
```

### Docker Integration

```dockerfile
# Add to Dockerfile
RUN apt-get update && apt-get install -y \
    v4l2loopback-dkms \
    v4l2loopback-utils \
    ffmpeg \
    xvfb

# Load v4l2loopback on container start
RUN echo "v4l2loopback" >> /etc/modules

# Start with privileged mode for device access
# docker run --privileged ...
```

---

For more information, see:
- [MCP Tools Reference](./MCP_TOOLS.md) - Complete MCP tool documentation
- [Testing Guide](./TESTING.md) - General testing documentation
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues and solutions