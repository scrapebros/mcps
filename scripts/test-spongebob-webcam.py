#!/usr/bin/env python3
"""
Test webcam with SpongeBob character as the video feed.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def test_spongebob_webcam():
    """Test webcam with SpongeBob video feed."""
    
    screenshot_dir = Path("/opt/mcp-playwright/reports/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    print("🧽 Launching browser with SpongeBob webcam...")
    
    async with async_playwright() as p:
        # Launch with SpongeBob Y4M video as fake webcam
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--use-fake-device-for-media-stream',
                '--use-file-for-fake-video-capture=/opt/mcp-playwright/webcam-assets/spongebob.y4m',
                '--use-fake-ui-for-media-stream',  # Auto-grant permissions
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        
        page = await context.new_page()
        
        print("📍 Navigating to webcamtests.com...")
        await page.goto("https://webcamtests.com/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Take initial screenshot
        await page.screenshot(path=str(screenshot_dir / "spongebob-1-initial.png"))
        print("  ✅ Screenshot 1: Page loaded")
        
        print("\n🎬 Starting SpongeBob webcam test...")
        
        # Click "Test my cam" button
        try:
            await page.click('button:has-text("Test my cam")', timeout=3000)
            print("  ✅ Clicked 'Test my cam'")
        except:
            print("  ⚠️ Test button not found or already active")
        
        # Wait for webcam to initialize
        await page.wait_for_timeout(3000)
        
        # Check video status
        print("\n🧽 Checking SpongeBob webcam status...")
        video_info = await page.evaluate("""() => {
            const video = document.querySelector('#webcam-stream') || document.querySelector('video');
            if (video) {
                let streamInfo = null;
                if (video.srcObject && video.srcObject.getTracks) {
                    const tracks = video.srcObject.getTracks();
                    streamInfo = tracks.map(t => ({
                        kind: t.kind,
                        label: t.label,
                        enabled: t.enabled
                    }));
                }
                
                return {
                    found: true,
                    playing: !video.paused,
                    hasStream: !!video.srcObject,
                    dimensions: `${video.videoWidth}x${video.videoHeight}`,
                    currentTime: video.currentTime,
                    streamInfo: streamInfo
                };
            }
            return { found: false };
        }""")
        
        print(f"  SpongeBob webcam status: {video_info}")
        
        if video_info['found'] and video_info['playing']:
            print("  🎉 SpongeBob is live on webcam!")
        
        # Take screenshots
        print("\n📸 Capturing SpongeBob webcam...")
        
        # Full page with SpongeBob
        await page.screenshot(path=str(screenshot_dir / "spongebob-2-webcam-active.png"), full_page=True)
        print("  ✅ Full page with SpongeBob webcam")
        
        # Try to capture just the video element
        try:
            video = page.locator('#webcam-stream, video').first
            if await video.is_visible():
                await video.screenshot(path=str(screenshot_dir / "spongebob-3-video-only.png"))
                print("  ✅ SpongeBob video element captured!")
        except Exception as e:
            print(f"  ⚠️ Could not capture video element: {e}")
        
        # Wait a bit more to ensure SpongeBob is fully visible
        await page.wait_for_timeout(2000)
        
        # Take another screenshot
        await page.screenshot(path=str(screenshot_dir / "spongebob-4-final.png"))
        print("  ✅ Final screenshot with SpongeBob")
        
        # Try to take a photo using the site's photo feature
        print("\n📷 Trying to take a photo with site's camera button...")
        try:
            await page.click('button:has-text("Take photo")', timeout=2000)
            await page.wait_for_timeout(1000)
            await page.screenshot(path=str(screenshot_dir / "spongebob-5-photo-taken.png"))
            print("  ✅ Photo taken with SpongeBob!")
        except:
            print("  ⚠️ Could not find photo button")
        
        print(f"\n🧽 SpongeBob webcam test completed!")
        print(f"📁 Screenshots saved in: {screenshot_dir}")
        print("\n🍍 Who lives in a pineapple under the sea? SPONGEBOB SQUAREPANTS!")
        
        await browser.close()

async def main():
    print("=" * 60)
    print("🧽 SpongeBob Webcam Test")
    print("=" * 60)
    print()
    await test_spongebob_webcam()

if __name__ == "__main__":
    asyncio.run(main())