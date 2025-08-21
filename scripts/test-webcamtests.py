#!/usr/bin/env python3
"""
Test webcam functionality on webcamtests.com
This script will start a fake webcam, navigate to webcamtests.com,
activate the webcam, and take a screenshot showing the test feed.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
import importlib.util
spec = importlib.util.spec_from_file_location("webcam_controller", "scripts/webcam-controller.py")
webcam_controller = importlib.util.module_from_spec(spec)
spec.loader.exec_module(webcam_controller)
WebcamController = webcam_controller.WebcamController

async def test_webcam_on_website():
    """Test webcam on webcamtests.com."""
    
    # Initialize webcam controller
    webcam = WebcamController("/dev/video20")
    
    try:
        print("🎥 Starting fake webcam with test pattern...")
        # Start webcam with SMPTE test pattern (professional color bars)
        result = webcam.stream_test_pattern("smpte")
        if not result.get("success"):
            print(f"❌ Failed to start webcam: {result.get('error')}")
            return
        
        print("✅ Webcam started successfully")
        
        # Give webcam time to initialize
        await asyncio.sleep(2)
        
        print("🌐 Launching browser...")
        async with async_playwright() as p:
            # Launch browser with webcam permissions
            browser = await p.chromium.launch(
                headless=True,  # Set to False to see the browser
                args=[
                    '--use-fake-device-for-media-stream',
                    '--use-file-for-fake-video-capture=/opt/mcp-playwright/webcam-assets/test-pattern.jpg',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            # Create context with camera permissions
            context = await browser.new_context(
                permissions=["camera", "microphone"],
                viewport={"width": 1920, "height": 1080}
            )
            
            page = await context.new_page()
            
            print("📍 Navigating to webcamtests.com...")
            await page.goto("https://webcamtests.com/", wait_until="networkidle")
            
            print("⏳ Waiting for page to load...")
            await page.wait_for_timeout(2000)
            
            # Check if there's a cookie consent or popup
            try:
                # Try to close any popup or cookie consent
                popup_selectors = [
                    'button:has-text("Accept")',
                    'button:has-text("OK")',
                    'button:has-text("Got it")',
                    '[aria-label="Close"]',
                    '.close-button',
                    '.modal-close'
                ]
                
                for selector in popup_selectors:
                    try:
                        if await page.locator(selector).is_visible():
                            await page.click(selector)
                            print(f"  Closed popup: {selector}")
                            break
                    except:
                        pass
            except:
                pass
            
            print("🎬 Looking for webcam test button...")
            
            # Try multiple selectors for the test button
            test_button_selectors = [
                'button:has-text("Test my cam")',
                'button:has-text("Test webcam")',
                'button:has-text("Check webcam")',
                'button:has-text("Start")',
                '#webcam-test',
                '.test-button',
                'button.btn-primary',
                'a:has-text("Test")'
            ]
            
            button_clicked = False
            for selector in test_button_selectors:
                try:
                    if await page.locator(selector).first.is_visible():
                        print(f"  Found button: {selector}")
                        await page.click(selector)
                        button_clicked = True
                        break
                except:
                    continue
            
            if not button_clicked:
                print("⚠️ Could not find test button, checking if webcam is already active...")
            
            # Wait for webcam to initialize
            await page.wait_for_timeout(3000)
            
            # Check for permission dialog and grant if needed
            try:
                # Some sites show their own permission UI
                allow_selectors = [
                    'button:has-text("Allow")',
                    'button:has-text("Grant")',
                    'button:has-text("Yes")',
                    'button:has-text("Continue")'
                ]
                
                for selector in allow_selectors:
                    try:
                        if await page.locator(selector).is_visible():
                            await page.click(selector)
                            print(f"  Granted permission: {selector}")
                            break
                    except:
                        pass
            except:
                pass
            
            # Wait for video element to appear and start streaming
            print("📹 Waiting for video feed...")
            
            video_selectors = [
                'video',
                '#video',
                '.video',
                'video#webcam',
                'video.webcam'
            ]
            
            video_found = False
            for selector in video_selectors:
                try:
                    if await page.locator(selector).first.is_visible():
                        print(f"  Found video element: {selector}")
                        video_found = True
                        
                        # Wait for video to start playing
                        await page.wait_for_function(
                            f"""() => {{
                                const video = document.querySelector('{selector}');
                                return video && video.readyState >= 2;
                            }}""",
                            timeout=10000
                        )
                        break
                except:
                    continue
            
            if not video_found:
                print("⚠️ No video element found, but taking screenshot anyway...")
            
            # Take multiple screenshots at different times
            screenshot_dir = Path("/opt/mcp-playwright/reports/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            print("📸 Taking screenshots...")
            
            # Full page screenshot
            screenshot_path1 = screenshot_dir / "webcamtests-full.png"
            await page.screenshot(path=str(screenshot_path1), full_page=True)
            print(f"  ✅ Full page screenshot: {screenshot_path1}")
            
            # Wait a bit more for video to stabilize
            await page.wait_for_timeout(2000)
            
            # Viewport screenshot (what's visible)
            screenshot_path2 = screenshot_dir / "webcamtests-viewport.png"
            await page.screenshot(path=str(screenshot_path2), full_page=False)
            print(f"  ✅ Viewport screenshot: {screenshot_path2}")
            
            # Try to capture just the video element if found
            if video_found:
                try:
                    video_element = page.locator('video').first
                    screenshot_path3 = screenshot_dir / "webcamtests-video.png"
                    await video_element.screenshot(path=str(screenshot_path3))
                    print(f"  ✅ Video element screenshot: {screenshot_path3}")
                except Exception as e:
                    print(f"  ⚠️ Could not capture video element: {e}")
            
            # Get page information
            print("\n📊 Page Information:")
            title = await page.title()
            print(f"  Title: {title}")
            
            # Check if webcam is detected
            webcam_status = await page.evaluate("""() => {
                const videos = document.querySelectorAll('video');
                const results = [];
                for (const video of videos) {
                    results.push({
                        src: video.src || video.srcObject ? 'Has source' : 'No source',
                        playing: !video.paused && !video.ended && video.readyState > 2,
                        dimensions: `${video.videoWidth}x${video.videoHeight}`,
                        visible: video.offsetWidth > 0 && video.offsetHeight > 0
                    });
                }
                return results;
            }""")
            
            if webcam_status:
                print("  Video elements found:")
                for i, status in enumerate(webcam_status):
                    print(f"    Video {i+1}: {status}")
            else:
                print("  No video elements detected")
            
            print("\n✅ Test completed successfully!")
            print(f"📁 Screenshots saved in: {screenshot_dir}")
            
            await browser.close()
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Stop the webcam
        print("\n🛑 Stopping webcam...")
        webcam.stop_stream()
        print("✅ Webcam stopped")

async def main():
    """Main entry point."""
    print("=" * 60)
    print("🎥 Webcam Test on webcamtests.com")
    print("=" * 60)
    print()
    
    # Check if virtual display is running
    display = os.environ.get('DISPLAY')
    if not display:
        print("⚠️ No DISPLAY set, setting to :99")
        os.environ['DISPLAY'] = ':99'
    
    print(f"📺 Using display: {os.environ['DISPLAY']}")
    
    # Run the test
    await test_webcam_on_website()

if __name__ == "__main__":
    asyncio.run(main())