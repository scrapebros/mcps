#!/usr/bin/env python3
"""
Test webcam functionality with Playwright Python
Demonstrates testing video applications with fake webcam
"""

import pytest
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright, expect
from scripts.webcam_controller import WebcamController

class TestWebcamIntegration:
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup webcam controller for tests."""
        self.webcam = WebcamController("/dev/video20")
        yield
        # Cleanup after test
        self.webcam.stop_stream()

    @pytest.mark.asyncio
    async def test_video_conferencing_with_fake_webcam(self):
        """Test video conferencing app with fake webcam."""
        async with async_playwright() as p:
            # Start fake webcam with test pattern
            result = self.webcam.stream_test_pattern("smpte")
            assert result["success"] is True

            # Launch browser with camera permissions
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                permissions=["camera"]
            )
            page = await context.new_page()

            # Create a simple video test page
            html = """
            <!DOCTYPE html>
            <html>
            <body>
                <h1>Camera Test</h1>
                <video id="video" autoplay></video>
                <button id="start">Start Camera</button>
                <div id="status">Not started</div>
                <script>
                    document.getElementById('start').onclick = async () => {
                        try {
                            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                            document.getElementById('video').srcObject = stream;
                            document.getElementById('status').textContent = 'Camera started';
                        } catch (err) {
                            document.getElementById('status').textContent = 'Error: ' + err.message;
                        }
                    };
                </script>
            </body>
            </html>
            """
            
            await page.goto(f"data:text/html,{html}")
            
            # Click start camera button
            await page.click("#start")
            
            # Wait for status to update
            await page.wait_for_selector("text=Camera started", timeout=5000)
            
            # Verify video element has stream
            has_stream = await page.evaluate("""
                () => {
                    const video = document.querySelector('#video');
                    return video && video.srcObject !== null;
                }
            """)
            assert has_stream is True
            
            # Take screenshot
            await page.screenshot(path="reports/screenshots/py-webcam-test.png")
            
            await browser.close()

    @pytest.mark.asyncio
    async def test_webcam_photo_capture(self):
        """Test capturing photos from fake webcam."""
        # Start webcam with custom image
        result = self.webcam.stream_color("red")
        assert result["success"] is True
        
        # Wait for stream to stabilize
        await asyncio.sleep(1)
        
        # Capture photo
        photo_result = self.webcam.capture_photo()
        assert photo_result["success"] is True
        assert photo_result["path"] is not None
        assert photo_result["data"] is not None  # Base64 data

    @pytest.mark.asyncio
    async def test_webcam_permission_handling(self):
        """Test different camera permission scenarios."""
        async with async_playwright() as p:
            # Test permission denial
            browser = await p.chromium.launch(headless=True)
            context_denied = await browser.new_context(
                permissions=[]  # No permissions granted
            )
            page_denied = await context_denied.new_page()
            
            html = """
            <!DOCTYPE html>
            <html>
            <body>
                <div id="result">Testing...</div>
                <script>
                    navigator.mediaDevices.getUserMedia({ video: true })
                        .then(() => {
                            document.getElementById('result').textContent = 'Camera access granted';
                        })
                        .catch(err => {
                            document.getElementById('result').textContent = 'Camera access denied: ' + err.name;
                        });
                </script>
            </body>
            </html>
            """
            
            await page_denied.goto(f"data:text/html,{html}")
            await page_denied.wait_for_selector("text=Camera access denied")
            
            result_denied = await page_denied.text_content("#result")
            assert "Camera access denied" in result_denied
            
            await context_denied.close()
            
            # Test permission grant
            self.webcam.stream_color("green")
            
            context_granted = await browser.new_context(
                permissions=["camera"]
            )
            page_granted = await context_granted.new_page()
            
            await page_granted.goto(f"data:text/html,{html}")
            await page_granted.wait_for_selector("text=Camera access granted", timeout=5000)
            
            result_granted = await page_granted.text_content("#result")
            assert "Camera access granted" in result_granted
            
            await browser.close()

    @pytest.mark.asyncio
    async def test_multiple_webcam_streams(self):
        """Test managing multiple webcam devices."""
        webcam1 = WebcamController("/dev/video20")
        webcam2 = WebcamController("/dev/video21")
        
        try:
            # Start first webcam with color
            result1 = webcam1.stream_color("blue")
            assert result1["success"] is True
            
            # Start second webcam with pattern
            result2 = webcam2.stream_test_pattern("testsrc")
            assert result2["success"] is True
            
            # Check status of both
            status1 = webcam1.get_status()
            status2 = webcam2.get_status()
            
            assert status1["streaming"] is True
            assert status2["streaming"] is True
            
        finally:
            # Cleanup
            webcam1.stop_stream()
            webcam2.stop_stream()

    @pytest.mark.asyncio
    async def test_webcam_in_real_video_app(self):
        """Test webcam with a real video conferencing page simulation."""
        async with async_playwright() as p:
            # Start webcam with video file
            result = self.webcam.stream_test_pattern("testsrc2")
            assert result["success"] is True
            
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                permissions=["camera", "microphone"],
                viewport={"width": 1280, "height": 720}
            )
            page = await context.new_page()
            
            # Create a more realistic video conference UI
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .video-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
                    .video-wrapper { background: #000; border-radius: 8px; overflow: hidden; position: relative; }
                    video { width: 100%; height: auto; display: block; }
                    .controls { background: #333; padding: 10px; text-align: center; }
                    button { margin: 0 5px; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
                    .btn-primary { background: #4CAF50; color: white; }
                    .btn-danger { background: #f44336; color: white; }
                    .status { color: #666; margin-top: 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Video Conference Test</h1>
                    <div class="video-grid">
                        <div class="video-wrapper">
                            <video id="localVideo" autoplay muted></video>
                            <div class="controls">
                                <button id="startBtn" class="btn-primary">Start Camera</button>
                                <button id="stopBtn" class="btn-danger" disabled>Stop Camera</button>
                            </div>
                        </div>
                        <div class="video-wrapper">
                            <video id="remoteVideo" autoplay></video>
                            <div class="controls">
                                <button id="simulateBtn" class="btn-primary">Simulate Remote</button>
                            </div>
                        </div>
                    </div>
                    <div id="status" class="status">Ready to start...</div>
                </div>
                <script>
                    let localStream = null;
                    
                    document.getElementById('startBtn').onclick = async () => {
                        try {
                            localStream = await navigator.mediaDevices.getUserMedia({ 
                                video: { width: 1280, height: 720 }, 
                                audio: false 
                            });
                            document.getElementById('localVideo').srcObject = localStream;
                            document.getElementById('status').textContent = 'Camera active';
                            document.getElementById('startBtn').disabled = true;
                            document.getElementById('stopBtn').disabled = false;
                        } catch (err) {
                            document.getElementById('status').textContent = 'Error: ' + err.message;
                        }
                    };
                    
                    document.getElementById('stopBtn').onclick = () => {
                        if (localStream) {
                            localStream.getTracks().forEach(track => track.stop());
                            document.getElementById('localVideo').srcObject = null;
                            document.getElementById('status').textContent = 'Camera stopped';
                            document.getElementById('startBtn').disabled = false;
                            document.getElementById('stopBtn').disabled = true;
                        }
                    };
                    
                    document.getElementById('simulateBtn').onclick = async () => {
                        // Simulate remote video by using same stream
                        if (localStream) {
                            document.getElementById('remoteVideo').srcObject = localStream.clone();
                            document.getElementById('status').textContent = 'Simulating remote participant';
                        }
                    };
                </script>
            </body>
            </html>
            """
            
            await page.goto(f"data:text/html,{html}")
            
            # Start local camera
            await page.click("#startBtn")
            await page.wait_for_selector("text=Camera active", timeout=5000)
            
            # Simulate remote participant
            await page.click("#simulateBtn")
            await page.wait_for_selector("text=Simulating remote participant")
            
            # Verify both videos are playing
            videos_playing = await page.evaluate("""
                () => {
                    const local = document.querySelector('#localVideo');
                    const remote = document.querySelector('#remoteVideo');
                    return {
                        local: local && local.srcObject !== null,
                        remote: remote && remote.srcObject !== null
                    };
                }
            """)
            
            assert videos_playing["local"] is True
            assert videos_playing["remote"] is True
            
            # Take screenshot of the conference
            await page.screenshot(path="reports/screenshots/py-conference-test.png")
            
            # Stop camera
            await page.click("#stopBtn")
            await page.wait_for_selector("text=Camera stopped")
            
            await browser.close()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])