#!/usr/bin/env python3
"""
Interactive webcam test with live page inspection.
Connects via WebSocket for debugging and properly activates webcam.
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def test_webcam_interactive():
    """Test webcam with interactive debugging."""
    
    screenshot_dir = Path("/opt/mcp-playwright/reports/screenshots")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    print("🌐 Launching browser in debug mode...")
    
    async with async_playwright() as p:
        # Launch browser with debugging port and fake webcam
        browser = await p.chromium.launch(
            headless=True,  # Run headless in server environment
            args=[
                '--use-fake-device-for-media-stream',
                '--use-file-for-fake-video-capture=/opt/mcp-playwright/webcam-assets/test-video.mp4',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--remote-debugging-port=9222',  # Enable CDP
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        # Create context with permissions
        context = await browser.new_context(
            permissions=["camera", "microphone"],
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"  📝 Console: {msg.text}"))
        page.on("pageerror", lambda err: print(f"  ❌ Error: {err}"))
        
        print("📍 Navigating to webcamtests.com...")
        await page.goto("https://webcamtests.com/", wait_until="networkidle")
        
        print("⏳ Waiting for page to fully load...")
        await page.wait_for_timeout(3000)
        
        # Inspect the page structure
        print("\n🔍 Inspecting page structure...")
        
        # Find all buttons and clickable elements
        buttons_info = await page.evaluate("""() => {
            const buttons = Array.from(document.querySelectorAll('button, a.btn, [role="button"], .test-button'));
            return buttons.map(btn => ({
                text: btn.innerText || btn.textContent,
                id: btn.id,
                class: btn.className,
                onclick: btn.onclick ? 'has onclick' : 'no onclick',
                href: btn.href || null,
                visible: btn.offsetWidth > 0 && btn.offsetHeight > 0
            }));
        }""")
        
        print(f"  Found {len(buttons_info)} buttons/clickable elements:")
        for btn in buttons_info:
            if btn['visible']:
                print(f"    - {btn}")
        
        # Check for iframes
        iframes = await page.query_selector_all('iframe')
        print(f"\n  Found {len(iframes)} iframe(s)")
        
        # Look for webcam-specific elements
        print("\n🎥 Looking for webcam elements...")
        webcam_elements = await page.evaluate("""() => {
            const elements = {
                videos: document.querySelectorAll('video').length,
                webcamDivs: document.querySelectorAll('[id*="webcam"], [class*="webcam"], [id*="camera"], [class*="camera"]').length,
                mediaElements: document.querySelectorAll('[id*="media"], [class*="media"]').length
            };
            return elements;
        }""")
        print(f"  Webcam-related elements: {webcam_elements}")
        
        # Try different methods to activate webcam
        print("\n🚀 Attempting to activate webcam...")
        
        # Method 1: Click the main test button
        try:
            # Look for the specific webcam test button
            test_button = await page.query_selector('#webcam-launcher')
            if test_button:
                print("  Found #webcam-launcher, clicking...")
                await test_button.click()
                await page.wait_for_timeout(3000)
            else:
                # Try text-based selector
                await page.click('text="Test my cam"', timeout=5000)
                print("  Clicked 'Test my cam' button")
                await page.wait_for_timeout(3000)
        except:
            print("  Could not find primary test button")
        
        # Method 2: Check if we need to grant permissions in the page UI
        print("\n🔐 Checking for permission prompts...")
        try:
            # Look for allow/grant buttons
            permission_selectors = [
                'button:has-text("Allow")',
                'button:has-text("Grant")',
                'button:has-text("Start")',
                'button:has-text("Enable")',
                '[class*="allow"]',
                '[class*="grant"]',
                '[class*="start"]'
            ]
            
            for selector in permission_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.click()
                        print(f"  Clicked permission element: {selector}")
                        await page.wait_for_timeout(2000)
                        break
                except:
                    continue
        except:
            pass
        
        # Method 3: Directly call getUserMedia via JavaScript
        print("\n💉 Injecting getUserMedia call...")
        media_result = await page.evaluate("""async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: true, 
                    audio: false 
                });
                
                // Find or create video element
                let video = document.querySelector('video#webcam-stream') || document.querySelector('video');
                if (!video) {
                    video = document.createElement('video');
                    video.id = 'injected-video';
                    video.autoplay = true;
                    video.style.width = '640px';
                    video.style.height = '480px';
                    document.body.appendChild(video);
                }
                
                video.srcObject = stream;
                await video.play();
                
                return {
                    success: true,
                    videoId: video.id,
                    streamActive: stream.active,
                    tracks: stream.getTracks().map(t => ({
                        kind: t.kind,
                        enabled: t.enabled,
                        label: t.label,
                        readyState: t.readyState
                    }))
                };
            } catch (err) {
                return {
                    success: false,
                    error: err.name + ': ' + err.message
                };
            }
        }""")
        
        print(f"  getUserMedia result: {media_result}")
        
        # Wait for video to stabilize
        await page.wait_for_timeout(3000)
        
        # Check video status again
        print("\n📹 Checking video status...")
        video_status = await page.evaluate("""() => {
            const videos = Array.from(document.querySelectorAll('video'));
            return videos.map((video, index) => ({
                index: index,
                id: video.id,
                hasStream: !!video.srcObject,
                streamActive: video.srcObject ? video.srcObject.active : false,
                playing: !video.paused && !video.ended,
                currentTime: video.currentTime,
                dimensions: `${video.videoWidth}x${video.videoHeight}`,
                visible: video.offsetWidth > 0 && video.offsetHeight > 0,
                readyState: video.readyState,
                networkState: video.networkState
            }));
        }""")
        
        print("  Video elements status:")
        for status in video_status:
            print(f"    {status}")
        
        # Check if webcam test result is displayed
        print("\n📊 Looking for test results...")
        test_results = await page.evaluate("""() => {
            const results = [];
            
            // Look for elements that might contain test results
            const resultSelectors = [
                '.test-result',
                '.result',
                '#result',
                '[class*="result"]',
                '[id*="result"]',
                '.status',
                '#status'
            ];
            
            for (const selector of resultSelectors) {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    if (el.textContent.trim()) {
                        results.push({
                            selector: selector,
                            text: el.textContent.trim().substring(0, 100)
                        });
                    }
                });
            }
            
            return results;
        }""")
        
        if test_results:
            print("  Test results found:")
            for result in test_results:
                print(f"    {result}")
        
        # Take screenshots
        print("\n📸 Taking screenshots...")
        
        # Full page screenshot
        screenshot_path1 = screenshot_dir / "webcam-interactive-full.png"
        await page.screenshot(path=str(screenshot_path1), full_page=True)
        print(f"  ✅ Full page: {screenshot_path1}")
        
        # Viewport screenshot
        screenshot_path2 = screenshot_dir / "webcam-interactive-viewport.png"
        await page.screenshot(path=str(screenshot_path2), full_page=False)
        print(f"  ✅ Viewport: {screenshot_path2}")
        
        # Try to capture video elements
        videos = await page.query_selector_all('video')
        for i, video in enumerate(videos):
            try:
                if await video.is_visible():
                    screenshot_path3 = screenshot_dir / f"webcam-interactive-video-{i}.png"
                    await video.screenshot(path=str(screenshot_path3))
                    print(f"  ✅ Video {i}: {screenshot_path3}")
            except:
                pass
        
        # Check device enumeration
        print("\n🎛️ Enumerating media devices...")
        devices = await page.evaluate("""async () => {
            try {
                const devices = await navigator.mediaDevices.enumerateDevices();
                return devices.map(d => ({
                    kind: d.kind,
                    label: d.label || 'Unnamed',
                    deviceId: d.deviceId.substring(0, 10) + '...'
                }));
            } catch (err) {
                return { error: err.message };
            }
        }""")
        
        print("  Available devices:")
        if isinstance(devices, list):
            for device in devices:
                print(f"    {device}")
        else:
            print(f"    Error: {devices}")
        
        # Try webcamtests.com specific API
        print("\n🔧 Checking for webcamtests.com specific functions...")
        api_check = await page.evaluate("""() => {
            const funcs = [];
            // Check for global functions related to webcam
            for (const key in window) {
                if (key.toLowerCase().includes('webcam') || 
                    key.toLowerCase().includes('camera') ||
                    key.toLowerCase().includes('test') ||
                    key.toLowerCase().includes('start')) {
                    funcs.push(key);
                }
            }
            return funcs;
        }""")
        
        if api_check:
            print(f"  Found functions: {api_check}")
        
        print("\n✅ Interactive test completed!")
        print(f"📁 Screenshots saved in: {screenshot_dir}")
        
        # Keep browser open for a moment to observe
        await page.wait_for_timeout(5000)
        
        await browser.close()

async def main():
    """Main entry point."""
    print("=" * 60)
    print("🎥 Interactive Webcam Test with Live Inspection")
    print("=" * 60)
    print()
    
    # Ensure we have a display
    if not os.environ.get('DISPLAY'):
        os.environ['DISPLAY'] = ':99'
        print(f"📺 Set DISPLAY to :99")
    
    await test_webcam_interactive()

if __name__ == "__main__":
    asyncio.run(main())