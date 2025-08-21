#!/usr/bin/env python3
"""
Final webcam test using Playwright's fake media stream capabilities.
This properly sets up fake devices and activates the webcam.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def test_webcam_final():
    """Test webcam with proper fake device setup."""
    
    screenshot_dir = Path("/opt/mcp-playwright/reports/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    print("🌐 Launching browser with fake media devices...")
    
    async with async_playwright() as p:
        # Launch with fake media stream that generates a test pattern
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--use-fake-device-for-media-stream',  # This enables fake devices
                '--use-fake-ui-for-media-stream',      # Auto-grant permissions
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Create context - permissions will be auto-granted due to fake-ui flag
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        
        page = await context.new_page()
        
        print("📍 Navigating to webcamtests.com...")
        await page.goto("https://webcamtests.com/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # Take initial screenshot
        await page.screenshot(path=str(screenshot_dir / "final-1-loaded.png"))
        print("  ✅ Screenshot 1: Page loaded")
        
        print("\n🎬 Starting webcam test...")
        
        # The page should have a "Test my cam" button or similar
        # First, let's check what's available
        buttons = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('button')).map(b => ({
                text: b.textContent.trim(),
                id: b.id,
                visible: b.offsetWidth > 0
            }));
        }""")
        print(f"  Available buttons: {[b['text'] for b in buttons if b['visible']]}")
        
        # Click "Test my cam" if available
        try:
            await page.click('button:has-text("Test my cam")', timeout=3000)
            print("  ✅ Clicked 'Test my cam'")
            await page.wait_for_timeout(2000)
        except:
            print("  ⚠️ 'Test my cam' button not found or already clicked")
        
        await page.screenshot(path=str(screenshot_dir / "final-2-after-test-button.png"))
        
        # Since we have --use-fake-ui-for-media-stream, permissions are auto-granted
        # The webcam should start automatically
        print("\n📹 Checking webcam status...")
        
        # Wait a bit for the stream to initialize
        await page.wait_for_timeout(3000)
        
        # Check video element status
        video_info = await page.evaluate("""() => {
            const video = document.querySelector('#webcam-stream') || document.querySelector('video');
            if (video) {
                // Try to get stream info
                let streamInfo = null;
                if (video.srcObject && video.srcObject.getTracks) {
                    const tracks = video.srcObject.getTracks();
                    streamInfo = tracks.map(t => ({
                        kind: t.kind,
                        enabled: t.enabled,
                        label: t.label,
                        readyState: t.readyState,
                        muted: t.muted
                    }));
                }
                
                return {
                    found: true,
                    id: video.id,
                    playing: !video.paused && !video.ended,
                    hasStream: !!video.srcObject,
                    currentTime: video.currentTime,
                    duration: video.duration,
                    dimensions: `${video.videoWidth}x${video.videoHeight}`,
                    readyState: video.readyState,
                    visible: video.offsetWidth > 0,
                    streamInfo: streamInfo
                };
            }
            return { found: false };
        }""")
        
        print(f"  Video status: {video_info}")
        
        # If video is not playing, try to trigger it
        if video_info['found'] and not video_info['playing']:
            print("\n🔧 Video found but not playing, attempting to start...")
            
            # Try clicking Start button if it exists
            try:
                await page.click('button:has-text("Start")', timeout=2000)
                print("  ✅ Clicked Start")
                await page.wait_for_timeout(2000)
            except:
                pass
            
            # Try to play video directly
            await page.evaluate("""() => {
                const video = document.querySelector('video');
                if (video && video.play) {
                    video.play().catch(e => console.log('Play failed:', e));
                }
            }""")
        
        await page.screenshot(path=str(screenshot_dir / "final-3-after-start.png"))
        
        # Check for test results
        print("\n📊 Looking for test results...")
        
        # webcamtests.com shows results in specific elements
        results = await page.evaluate("""() => {
            const results = {};
            
            // Check for resolution info
            const resElement = document.querySelector('.webcam-resolution, #webcam-resolution, [class*="resolution"]');
            if (resElement) {
                results.resolution = resElement.textContent.trim();
            }
            
            // Check for FPS info
            const fpsElement = document.querySelector('.webcam-fps, #webcam-fps, [class*="fps"]');
            if (fpsElement) {
                results.fps = fpsElement.textContent.trim();
            }
            
            // Check for any test status
            const statusElements = document.querySelectorAll('.test-status, .status, [class*="status"], [class*="result"]');
            results.status = Array.from(statusElements).map(el => el.textContent.trim()).filter(t => t && t.length < 100);
            
            // Get video final state
            const video = document.querySelector('video');
            if (video) {
                results.videoPlaying = !video.paused;
                results.videoDimensions = `${video.videoWidth}x${video.videoHeight}`;
                results.videoTime = video.currentTime;
            }
            
            return results;
        }""")
        
        print(f"  Test results: {results}")
        
        # Take final screenshots
        print("\n📸 Taking final screenshots...")
        
        # Full page
        await page.screenshot(path=str(screenshot_dir / "final-4-complete.png"), full_page=True)
        print(f"  ✅ Full page: final-4-complete.png")
        
        # Just the video element if visible
        try:
            video = page.locator('#webcam-stream, video').first
            if await video.is_visible():
                await video.screenshot(path=str(screenshot_dir / "final-5-video.png"))
                print(f"  ✅ Video element: final-5-video.png")
        except:
            pass
        
        # Check what media devices are available
        print("\n🎛️ Media devices check...")
        devices = await page.evaluate("""async () => {
            try {
                const devices = await navigator.mediaDevices.enumerateDevices();
                return {
                    cameras: devices.filter(d => d.kind === 'videoinput').length,
                    microphones: devices.filter(d => d.kind === 'audioinput').length,
                    speakers: devices.filter(d => d.kind === 'audiooutput').length,
                    details: devices.map(d => `${d.kind}: ${d.label || 'Unnamed'}`)
                };
            } catch (e) {
                return { error: e.message };
            }
        }""")
        print(f"  Available devices: {devices}")
        
        print(f"\n✅ Test completed!")
        print(f"📁 Screenshots saved in: {screenshot_dir}")
        print("\n💡 Note: Chromium's fake media stream shows a green pattern with")
        print("   timestamp and 'Chromium' text when --use-fake-device-for-media-stream is used.")
        
        await browser.close()

async def main():
    print("=" * 60)
    print("🎥 Final Webcam Test with Fake Media Stream")
    print("=" * 60)
    print()
    await test_webcam_final()

if __name__ == "__main__":
    asyncio.run(main())