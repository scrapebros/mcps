#!/usr/bin/env python3
"""
Debug script to properly activate webcam on webcamtests.com
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def test_webcam_debug():
    """Debug webcam activation."""
    
    screenshot_dir = Path("/opt/mcp-playwright/reports/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    print("🌐 Launching browser with fake webcam...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--use-fake-device-for-media-stream',
                '--use-file-for-fake-video-capture=/opt/mcp-playwright/webcam-assets/test-video.mp4',
                '--use-fake-audio-capture',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        
        context = await browser.new_context(
            permissions=["camera", "microphone"]
        )
        
        page = await context.new_page()
        
        print("📍 Going to webcamtests.com...")
        await page.goto("https://webcamtests.com/")
        await page.wait_for_load_state("networkidle")
        
        # Take initial screenshot
        await page.screenshot(path=str(screenshot_dir / "debug-1-initial.png"))
        print("  ✅ Screenshot 1: Initial page")
        
        # Method 1: Try to click the webcam test button by ID
        print("\n🎯 Method 1: Click #webcam-launcher...")
        try:
            await page.click('#webcam-launcher', timeout=5000)
            print("  ✅ Clicked #webcam-launcher")
            await page.wait_for_timeout(3000)
        except:
            print("  ❌ Could not click #webcam-launcher")
        
        await page.screenshot(path=str(screenshot_dir / "debug-2-after-launcher.png"))
        
        # Method 2: Check for permission dialog within the page
        print("\n🎯 Method 2: Look for Start/Allow buttons...")
        try:
            # The site might show its own permission dialog
            start_button = page.locator('button:has-text("Start")').first
            if await start_button.is_visible():
                await start_button.click()
                print("  ✅ Clicked Start button")
                await page.wait_for_timeout(2000)
        except:
            print("  ❌ No Start button found")
        
        await page.screenshot(path=str(screenshot_dir / "debug-3-after-start.png"))
        
        # Method 3: Force getUserMedia through JavaScript
        print("\n🎯 Method 3: Force getUserMedia...")
        result = await page.evaluate("""async () => {
            try {
                // Request camera access
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        width: 640, 
                        height: 480 
                    }, 
                    audio: false 
                });
                
                // Find the video element on the page
                let video = document.querySelector('#webcam-stream');
                if (!video) {
                    video = document.querySelector('video');
                }
                
                if (video) {
                    video.srcObject = stream;
                    await video.play();
                    return { 
                        success: true, 
                        videoFound: true,
                        videoId: video.id,
                        playing: !video.paused
                    };
                } else {
                    // Create our own video element
                    video = document.createElement('video');
                    video.id = 'test-video';
                    video.autoplay = true;
                    video.srcObject = stream;
                    video.style.position = 'fixed';
                    video.style.top = '10px';
                    video.style.left = '10px';
                    video.style.width = '320px';
                    video.style.height = '240px';
                    video.style.zIndex = '9999';
                    document.body.appendChild(video);
                    await video.play();
                    return { 
                        success: true, 
                        videoFound: false,
                        created: true,
                        playing: !video.paused
                    };
                }
            } catch (err) {
                return { 
                    success: false, 
                    error: err.name + ': ' + err.message 
                };
            }
        }""")
        
        print(f"  Result: {result}")
        await page.wait_for_timeout(2000)
        
        await page.screenshot(path=str(screenshot_dir / "debug-4-after-getusermedia.png"))
        
        # Method 4: Check if the site has a specific flow
        print("\n🎯 Method 4: Check page state...")
        
        # Get all video elements
        videos = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('video')).map(v => ({
                id: v.id,
                src: v.src,
                hasStream: !!v.srcObject,
                playing: !v.paused,
                width: v.videoWidth,
                height: v.videoHeight,
                visible: v.offsetWidth > 0
            }));
        }""")
        
        print(f"  Videos found: {videos}")
        
        # Check for test results or status elements
        status = await page.evaluate("""() => {
            const statusElements = document.querySelectorAll('.status, #status, [class*="result"], [id*="result"]');
            return Array.from(statusElements).map(el => el.textContent.trim()).filter(t => t);
        }""")
        
        print(f"  Status elements: {status}")
        
        # Try to trigger the test by clicking on the video area
        print("\n🎯 Method 5: Click on video area...")
        try:
            video_element = page.locator('#webcam-stream').first
            if await video_element.is_visible():
                await video_element.click()
                print("  ✅ Clicked on video element")
                await page.wait_for_timeout(2000)
        except:
            print("  ❌ Could not click video element")
        
        await page.screenshot(path=str(screenshot_dir / "debug-5-final.png"))
        
        # Get final state
        print("\n📊 Final page state:")
        final_state = await page.evaluate("""() => {
            const state = {
                videos: document.querySelectorAll('video').length,
                buttons: Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim()),
                hasWebcamStream: !!document.querySelector('#webcam-stream'),
                mediaDevices: typeof navigator.mediaDevices !== 'undefined'
            };
            
            // Check if getUserMedia was called
            if (document.querySelector('video')) {
                const video = document.querySelector('video');
                state.videoState = {
                    hasSource: !!video.srcObject || !!video.src,
                    playing: !video.paused,
                    dimensions: `${video.videoWidth}x${video.videoHeight}`
                };
            }
            
            return state;
        }""")
        
        print(f"  {final_state}")
        
        print(f"\n✅ Debug complete! Check screenshots in {screenshot_dir}")
        
        await browser.close()

async def main():
    print("=" * 60)
    print("🔍 Webcam Debug Test")
    print("=" * 60)
    await test_webcam_debug()

if __name__ == "__main__":
    asyncio.run(main())