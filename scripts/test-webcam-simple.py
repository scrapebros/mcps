#!/usr/bin/env python3
"""
Simple webcam test using Playwright's built-in fake media capabilities.
Tests webcam on webcamtests.com without needing v4l2loopback.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def test_webcam_simple():
    """Test webcam using Playwright's fake media."""
    
    screenshot_dir = Path("/opt/mcp-playwright/reports/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    print("🌐 Launching browser with fake webcam...")
    
    async with async_playwright() as p:
        # Launch browser with fake webcam using test video
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--use-fake-device-for-media-stream',
                '--use-file-for-fake-video-capture=/opt/mcp-playwright/webcam-assets/test-video.mp4',
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
        await page.wait_for_timeout(3000)
        
        # Take initial screenshot
        screenshot_path = screenshot_dir / "webcamtests-initial.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"  ✅ Initial screenshot: {screenshot_path}")
        
        print("🎬 Looking for and clicking test button...")
        
        # Try to find and click the test webcam button
        try:
            # Look for the test button
            test_button = page.locator('button:has-text("Test my cam")').first
            if await test_button.is_visible():
                await test_button.click()
                print("  ✅ Clicked 'Test my cam' button")
            else:
                # Try alternative selector
                test_button = page.locator('#webcam-launcher').first
                if await test_button.is_visible():
                    await test_button.click()
                    print("  ✅ Clicked webcam launcher")
        except:
            print("  ⚠️ Could not find test button, proceeding...")
        
        # Wait for webcam to initialize
        await page.wait_for_timeout(5000)
        
        # Take screenshot after clicking test
        screenshot_path2 = screenshot_dir / "webcamtests-after-click.png"
        await page.screenshot(path=str(screenshot_path2), full_page=True)
        print(f"  ✅ After-click screenshot: {screenshot_path2}")
        
        # Check for video elements
        print("📹 Checking for video elements...")
        video_info = await page.evaluate("""() => {
            const videos = document.querySelectorAll('video');
            const results = [];
            for (const video of videos) {
                results.push({
                    id: video.id,
                    class: video.className,
                    src: video.src || 'MediaStream',
                    playing: !video.paused,
                    dimensions: `${video.videoWidth}x${video.videoHeight}`,
                    visible: video.offsetWidth > 0 && video.offsetHeight > 0,
                    currentTime: video.currentTime
                });
            }
            return results;
        }""")
        
        if video_info:
            print(f"  ✅ Found {len(video_info)} video element(s):")
            for i, info in enumerate(video_info):
                print(f"     Video {i+1}: {info}")
                
            # Try to capture just the video element
            try:
                video_element = page.locator('video').first
                if await video_element.is_visible():
                    screenshot_path3 = screenshot_dir / "webcamtests-video-element.png"
                    await video_element.screenshot(path=str(screenshot_path3))
                    print(f"  ✅ Video element screenshot: {screenshot_path3}")
            except:
                pass
        else:
            print("  ⚠️ No video elements found")
        
        # Take final full-page screenshot
        screenshot_path4 = screenshot_dir / "webcamtests-final.png"
        await page.screenshot(path=str(screenshot_path4), full_page=True)
        print(f"  ✅ Final screenshot: {screenshot_path4}")
        
        print("\n✅ Test completed successfully!")
        print(f"📁 Screenshots saved in: {screenshot_dir}")
        
        await browser.close()

async def main():
    """Main entry point."""
    print("=" * 60)
    print("🎥 Simple Webcam Test on webcamtests.com")
    print("=" * 60)
    print()
    
    await test_webcam_simple()

if __name__ == "__main__":
    asyncio.run(main())