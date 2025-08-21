#!/usr/bin/env python3
"""
Fake Webcam Controller for MCP Playwright
Controls virtual webcam devices for testing video applications
"""

import subprocess
import os
import sys
import time
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

class WebcamMode(Enum):
    IMAGE = "image"
    VIDEO = "video"
    SCREEN = "screen"
    TEST_PATTERN = "test_pattern"
    COLOR = "color"
    TEXT = "text"

class WebcamController:
    def __init__(self, device: str = "/dev/video20"):
        self.device = device
        self.assets_dir = Path("/opt/mcp-playwright/webcam-assets")
        self.ffmpeg_process: Optional[subprocess.Popen] = None
        self.current_mode: Optional[WebcamMode] = None
        
        # Ensure assets directory exists
        self.assets_dir.mkdir(exist_ok=True, parents=True)
    
    def check_device(self) -> bool:
        """Check if webcam device exists."""
        return os.path.exists(self.device)
    
    def list_devices(self) -> list:
        """List all video devices."""
        try:
            result = subprocess.run(
                ["v4l2-ctl", "--list-devices"],
                capture_output=True,
                text=True
            )
            return result.stdout.split('\n')
        except Exception as e:
            return [f"Error listing devices: {e}"]
    
    def stop_stream(self):
        """Stop current webcam stream."""
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            time.sleep(0.5)
            if self.ffmpeg_process.poll() is None:
                self.ffmpeg_process.kill()
            self.ffmpeg_process = None
            self.current_mode = None
    
    def stream_image(self, image_path: str, loop: bool = True) -> Dict[str, Any]:
        """Stream a static image to the webcam."""
        self.stop_stream()
        
        if not os.path.exists(image_path):
            # Use default test pattern
            image_path = self.assets_dir / "test-pattern.jpg"
            if not image_path.exists():
                self.create_test_pattern()
        
        cmd = [
            "ffmpeg",
            "-re",  # Real-time encoding
            "-loop", "1" if loop else "0",
            "-i", str(image_path),
            "-f", "v4l2",
            "-vcodec", "rawvideo",
            "-pix_fmt", "yuv420p",
            "-s", "640x480",
            "-r", "30",
            self.device
        ]
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.current_mode = WebcamMode.IMAGE
            time.sleep(1)  # Give it time to start
            
            return {
                "success": True,
                "mode": WebcamMode.IMAGE.value,
                "source": str(image_path),
                "device": self.device
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def stream_video(self, video_path: str, loop: bool = True) -> Dict[str, Any]:
        """Stream a video file to the webcam."""
        self.stop_stream()
        
        if not os.path.exists(video_path):
            video_path = self.assets_dir / "test-video.mp4"
            if not video_path.exists():
                self.create_test_video()
        
        cmd = [
            "ffmpeg",
            "-re",
            "-stream_loop", "-1" if loop else "0",
            "-i", str(video_path),
            "-f", "v4l2",
            "-vcodec", "rawvideo",
            "-pix_fmt", "yuv420p",
            self.device
        ]
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.current_mode = WebcamMode.VIDEO
            time.sleep(1)
            
            return {
                "success": True,
                "mode": WebcamMode.VIDEO.value,
                "source": str(video_path),
                "device": self.device
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def stream_screen(self, display: str = ":99") -> Dict[str, Any]:
        """Stream screen capture to webcam."""
        self.stop_stream()
        
        cmd = [
            "ffmpeg",
            "-f", "x11grab",
            "-r", "30",
            "-s", "1920x1080",
            "-i", display,
            "-vf", "scale=640:480",
            "-f", "v4l2",
            "-pix_fmt", "yuv420p",
            self.device
        ]
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.current_mode = WebcamMode.SCREEN
            time.sleep(1)
            
            return {
                "success": True,
                "mode": WebcamMode.SCREEN.value,
                "source": display,
                "device": self.device
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def stream_test_pattern(self, pattern: str = "smpte") -> Dict[str, Any]:
        """Stream a test pattern to webcam."""
        self.stop_stream()
        
        # Patterns: smpte, testsrc, testsrc2, rgbtestsrc, smptebars
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"{pattern}=size=640x480:rate=30",
            "-f", "v4l2",
            "-pix_fmt", "yuv420p",
            self.device
        ]
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.current_mode = WebcamMode.TEST_PATTERN
            time.sleep(1)
            
            return {
                "success": True,
                "mode": WebcamMode.TEST_PATTERN.value,
                "pattern": pattern,
                "device": self.device
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def stream_color(self, color: str = "blue") -> Dict[str, Any]:
        """Stream a solid color to webcam."""
        self.stop_stream()
        
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c={color}:size=640x480:rate=30",
            "-f", "v4l2",
            "-pix_fmt", "yuv420p",
            self.device
        ]
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.current_mode = WebcamMode.COLOR
            time.sleep(1)
            
            return {
                "success": True,
                "mode": WebcamMode.COLOR.value,
                "color": color,
                "device": self.device
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_test_pattern(self):
        """Create a test pattern image."""
        cmd = [
            "convert",
            "-size", "640x480",
            "xc:blue",
            "-fill", "white",
            "-pointsize", "48",
            "-draw", "text 100,240 'MCP Playwright Webcam'",
            str(self.assets_dir / "test-pattern.jpg")
        ]
        subprocess.run(cmd, check=True)
    
    def create_test_video(self):
        """Create a test video."""
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", "testsrc=duration=10:size=640x480:rate=30",
            "-pix_fmt", "yuv420p",
            str(self.assets_dir / "test-video.mp4"),
            "-y"
        ]
        subprocess.run(cmd, check=True)
    
    def create_custom_image(self, text: str, bg_color: str = "lightblue") -> str:
        """Create a custom image with text."""
        output_path = self.assets_dir / f"custom_{int(time.time())}.jpg"
        
        cmd = [
            "convert",
            "-size", "640x480",
            f"xc:{bg_color}",
            "-fill", "black",
            "-pointsize", "36",
            "-gravity", "center",
            "-draw", f"text 0,0 '{text}'",
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True)
        return str(output_path)
    
    def capture_photo(self) -> Dict[str, Any]:
        """Capture a photo from the webcam."""
        output_path = self.assets_dir / f"capture_{int(time.time())}.jpg"
        
        cmd = [
            "ffmpeg",
            "-f", "v4l2",
            "-i", self.device,
            "-frames:v", "1",
            str(output_path),
            "-y"
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Read and encode image
            with open(output_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            return {
                "success": True,
                "path": str(output_path),
                "data": image_data,
                "device": self.device
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current webcam status."""
        return {
            "device": self.device,
            "exists": self.check_device(),
            "streaming": self.ffmpeg_process is not None,
            "mode": self.current_mode.value if self.current_mode else None,
            "process_running": self.ffmpeg_process.poll() is None if self.ffmpeg_process else False
        }


def main():
    """CLI interface for webcam controller."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Control fake webcam for testing")
    parser.add_argument("command", choices=[
        "start", "stop", "status", "list", "capture",
        "image", "video", "screen", "pattern", "color", "text"
    ])
    parser.add_argument("--device", default="/dev/video20", help="Video device")
    parser.add_argument("--source", help="Source file or value")
    parser.add_argument("--loop", action="store_true", help="Loop media")
    parser.add_argument("--display", default=":99", help="Display for screen capture")
    
    args = parser.parse_args()
    
    controller = WebcamController(args.device)
    
    if args.command == "list":
        devices = controller.list_devices()
        print("\n".join(devices))
    
    elif args.command == "status":
        status = controller.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.command == "stop":
        controller.stop_stream()
        print("Webcam stream stopped")
    
    elif args.command == "image":
        source = args.source or "/opt/mcp-playwright/webcam-assets/test-pattern.jpg"
        result = controller.stream_image(source, args.loop)
        print(json.dumps(result, indent=2))
    
    elif args.command == "video":
        source = args.source or "/opt/mcp-playwright/webcam-assets/test-video.mp4"
        result = controller.stream_video(source, args.loop)
        print(json.dumps(result, indent=2))
    
    elif args.command == "screen":
        result = controller.stream_screen(args.display)
        print(json.dumps(result, indent=2))
    
    elif args.command == "pattern":
        pattern = args.source or "smpte"
        result = controller.stream_test_pattern(pattern)
        print(json.dumps(result, indent=2))
    
    elif args.command == "color":
        color = args.source or "blue"
        result = controller.stream_color(color)
        print(json.dumps(result, indent=2))
    
    elif args.command == "text":
        text = args.source or "Hello from MCP Playwright"
        image_path = controller.create_custom_image(text)
        result = controller.stream_image(image_path)
        print(json.dumps(result, indent=2))
    
    elif args.command == "capture":
        result = controller.capture_photo()
        if result["success"]:
            print(f"Photo captured: {result['path']}")
        else:
            print(f"Capture failed: {result['error']}")
    
    elif args.command == "start":
        # Default start with test pattern
        result = controller.stream_test_pattern()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()