/**
 * Test script for webcam functionality with Playwright
 * Demonstrates testing video applications with fake webcam
 */

import { test, expect } from '@playwright/test';
import { WebcamManager } from '../src/webcam-tools';

test.describe('Webcam Integration Tests', () => {
  let webcamManager: WebcamManager;

  test.beforeAll(async () => {
    webcamManager = new WebcamManager();
  });

  test.afterAll(async () => {
    await webcamManager.cleanup();
  });

  test('test video conferencing app with fake webcam', async ({ page, context }) => {
    // Grant camera permissions
    await context.grantPermissions(['camera']);

    // Start fake webcam with test pattern
    const result = await webcamManager.startWebcam({
      mode: 'pattern',
      source: 'smpte',
      device: '/dev/video20'
    });
    
    expect(result.success).toBe(true);

    // Navigate to a video test page
    // For demo, we'll create a simple page that accesses the camera
    await page.goto('data:text/html,<!DOCTYPE html><html><body><h1>Camera Test</h1><video id="video" autoplay></video><button id="start">Start Camera</button><script>document.getElementById("start").onclick = async () => { const stream = await navigator.mediaDevices.getUserMedia({ video: true }); document.getElementById("video").srcObject = stream; };</script></body></html>');

    // Click start camera button
    await page.click('#start');

    // Wait for video element to have stream
    await page.waitForFunction(() => {
      const video = document.querySelector('#video') as HTMLVideoElement;
      return video && video.srcObject !== null;
    });

    // Take screenshot of the page with video
    await page.screenshot({ path: 'reports/screenshots/webcam-test.png' });

    // Verify video is playing
    const isPlaying = await page.evaluate(() => {
      const video = document.querySelector('#video') as HTMLVideoElement;
      return !!(video.currentTime > 0 && !video.paused && !video.ended && video.readyState > 2);
    });

    expect(isPlaying).toBe(true);

    // Stop the webcam
    webcamManager.stopWebcam('/dev/video20');
  });

  test('test webcam photo capture', async ({ page, context }) => {
    // Start webcam with custom text image
    const result = await webcamManager.startWebcam({
      mode: 'text',
      source: 'MCP Playwright Test',
      device: '/dev/video20'
    });
    
    expect(result.success).toBe(true);

    // Capture a photo from the webcam
    const photoResult = await webcamManager.capturePhoto('/dev/video20');
    
    expect(photoResult.success).toBe(true);
    expect(photoResult.data?.path).toBeTruthy();
    expect(photoResult.data?.base64).toBeTruthy();

    // Clean up
    webcamManager.stopWebcam('/dev/video20');
  });

  test('test multiple webcam devices', async ({ page }) => {
    // Start first webcam with color
    const webcam1 = await webcamManager.startWebcam({
      mode: 'color',
      source: 'blue',
      device: '/dev/video20'
    });
    
    expect(webcam1.success).toBe(true);

    // Start second webcam with pattern
    const webcam2 = await webcamManager.startWebcam({
      mode: 'pattern',
      source: 'testsrc',
      device: '/dev/video21'
    });
    
    expect(webcam2.success).toBe(true);

    // Check status of both webcams
    const status1 = await webcamManager.getStatus('/dev/video20');
    const status2 = await webcamManager.getStatus('/dev/video21');
    
    expect(status1.streaming).toBe(true);
    expect(status2.streaming).toBe(true);

    // Clean up
    webcamManager.stopWebcam('/dev/video20');
    webcamManager.stopWebcam('/dev/video21');
  });

  test('test screen capture to webcam', async ({ page, context }) => {
    // Start virtual display if not already running
    await page.goto('https://example.com');
    
    // Start screen capture to webcam
    const result = await webcamManager.startWebcam({
      mode: 'screen',
      source: ':99', // Xvfb display
      device: '/dev/video20'
    });
    
    if (result.success) {
      // Grant camera permissions
      await context.grantPermissions(['camera']);

      // Create a page that shows the webcam feed
      await page.goto('data:text/html,<!DOCTYPE html><html><body><video id="video" autoplay style="width:100%"></video><script>navigator.mediaDevices.getUserMedia({ video: true }).then(stream => document.getElementById("video").srcObject = stream);</script></body></html>');

      // Wait for video to load
      await page.waitForTimeout(2000);

      // Take screenshot
      await page.screenshot({ path: 'reports/screenshots/screen-to-webcam.png' });

      // Clean up
      webcamManager.stopWebcam('/dev/video20');
    }
  });
});

test.describe('Webcam Permissions Tests', () => {
  test('test camera permission denial', async ({ page, context }) => {
    // Deny camera permissions
    await context.grantPermissions([]);

    await page.goto('data:text/html,<!DOCTYPE html><html><body><h1>Camera Permission Test</h1><div id="result"></div><script>navigator.mediaDevices.getUserMedia({ video: true }).then(() => { document.getElementById("result").textContent = "Camera access granted"; }).catch(err => { document.getElementById("result").textContent = "Camera access denied: " + err.name; });</script></body></html>');

    // Wait for result
    await page.waitForSelector('#result');
    
    const result = await page.textContent('#result');
    expect(result).toContain('Camera access denied');
  });

  test('test camera permission grant', async ({ page, context }) => {
    // Grant camera permissions
    await context.grantPermissions(['camera']);

    // Start a fake webcam
    const webcamManager = new WebcamManager();
    await webcamManager.startWebcam({
      mode: 'color',
      source: 'green',
      device: '/dev/video20'
    });

    await page.goto('data:text/html,<!DOCTYPE html><html><body><h1>Camera Permission Test</h1><div id="result"></div><script>navigator.mediaDevices.getUserMedia({ video: true }).then(() => { document.getElementById("result").textContent = "Camera access granted"; }).catch(err => { document.getElementById("result").textContent = "Camera access denied: " + err.name; });</script></body></html>');

    // Wait for result
    await page.waitForSelector('#result');
    
    const result = await page.textContent('#result');
    expect(result).toContain('Camera access granted');

    // Clean up
    webcamManager.stopWebcam('/dev/video20');
  });
});