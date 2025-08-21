/**
 * Webcam Tools for MCP Playwright
 * Provides webcam control and simulation capabilities
 */

import { exec, spawn, ChildProcess } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs/promises';
import * as path from 'path';

const execAsync = promisify(exec);

export interface WebcamStatus {
  device: string;
  exists: boolean;
  streaming: boolean;
  mode: string | null;
}

export interface WebcamResult {
  success: boolean;
  message?: string;
  error?: string;
  data?: any;
}

export class WebcamManager {
  private ffmpegProcesses: Map<string, ChildProcess> = new Map();
  private assetsDir = '/opt/mcp-playwright/webcam-assets';

  async checkDevice(device: string = '/dev/video20'): Promise<boolean> {
    try {
      await fs.access(device);
      return true;
    } catch {
      return false;
    }
  }

  async listDevices(): Promise<string[]> {
    try {
      const { stdout } = await execAsync('v4l2-ctl --list-devices');
      return stdout.split('\n').filter(line => line.includes('/dev/video'));
    } catch (error) {
      return [];
    }
  }

  async startWebcam(params: {
    device?: string;
    mode: 'image' | 'video' | 'pattern' | 'color' | 'screen' | 'text';
    source?: string;
    loop?: boolean;
  }): Promise<WebcamResult> {
    const device = params.device || '/dev/video20';
    
    // Stop any existing stream on this device
    this.stopWebcam(device);

    let command: string[];
    
    switch (params.mode) {
      case 'image':
        const imagePath = params.source || `${this.assetsDir}/test-pattern.jpg`;
        command = [
          'ffmpeg',
          '-re',
          '-loop', params.loop ? '1' : '0',
          '-i', imagePath,
          '-f', 'v4l2',
          '-vcodec', 'rawvideo',
          '-pix_fmt', 'yuv420p',
          '-s', '640x480',
          '-r', '30',
          device
        ];
        break;

      case 'video':
        const videoPath = params.source || `${this.assetsDir}/test-video.mp4`;
        command = [
          'ffmpeg',
          '-re',
          '-stream_loop', params.loop ? '-1' : '0',
          '-i', videoPath,
          '-f', 'v4l2',
          '-vcodec', 'rawvideo',
          '-pix_fmt', 'yuv420p',
          device
        ];
        break;

      case 'pattern':
        const pattern = params.source || 'smpte';
        command = [
          'ffmpeg',
          '-f', 'lavfi',
          '-i', `${pattern}=size=640x480:rate=30`,
          '-f', 'v4l2',
          '-pix_fmt', 'yuv420p',
          device
        ];
        break;

      case 'color':
        const color = params.source || 'blue';
        command = [
          'ffmpeg',
          '-f', 'lavfi',
          '-i', `color=c=${color}:size=640x480:rate=30`,
          '-f', 'v4l2',
          '-pix_fmt', 'yuv420p',
          device
        ];
        break;

      case 'screen':
        const display = params.source || ':99';
        command = [
          'ffmpeg',
          '-f', 'x11grab',
          '-r', '30',
          '-s', '1920x1080',
          '-i', display,
          '-vf', 'scale=640:480',
          '-f', 'v4l2',
          '-pix_fmt', 'yuv420p',
          device
        ];
        break;

      case 'text':
        const text = params.source || 'MCP Playwright Webcam';
        const textImagePath = await this.createTextImage(text);
        command = [
          'ffmpeg',
          '-re',
          '-loop', '1',
          '-i', textImagePath,
          '-f', 'v4l2',
          '-vcodec', 'rawvideo',
          '-pix_fmt', 'yuv420p',
          '-s', '640x480',
          '-r', '30',
          device
        ];
        break;

      default:
        return {
          success: false,
          error: `Unknown mode: ${params.mode}`
        };
    }

    try {
      const ffmpeg = spawn(command[0], command.slice(1), {
        stdio: ['ignore', 'pipe', 'pipe']
      });

      this.ffmpegProcesses.set(device, ffmpeg);

      // Give it a moment to start
      await new Promise(resolve => setTimeout(resolve, 1000));

      return {
        success: true,
        message: `Webcam started in ${params.mode} mode on ${device}`,
        data: {
          device,
          mode: params.mode,
          source: params.source
        }
      };
    } catch (error) {
      return {
        success: false,
        error: `Failed to start webcam: ${error}`
      };
    }
  }

  stopWebcam(device: string = '/dev/video20'): void {
    const process = this.ffmpegProcesses.get(device);
    if (process) {
      process.kill('SIGTERM');
      this.ffmpegProcesses.delete(device);
    }
  }

  async capturePhoto(device: string = '/dev/video20'): Promise<WebcamResult> {
    const timestamp = Date.now();
    const outputPath = path.join(this.assetsDir, `capture_${timestamp}.jpg`);

    try {
      await execAsync(`ffmpeg -f v4l2 -i ${device} -frames:v 1 ${outputPath} -y`);
      
      const imageData = await fs.readFile(outputPath);
      const base64 = imageData.toString('base64');

      return {
        success: true,
        message: 'Photo captured successfully',
        data: {
          path: outputPath,
          base64: base64,
          device: device
        }
      };
    } catch (error) {
      return {
        success: false,
        error: `Failed to capture photo: ${error}`
      };
    }
  }

  async getStatus(device: string = '/dev/video20'): Promise<WebcamStatus> {
    const exists = await this.checkDevice(device);
    const process = this.ffmpegProcesses.get(device);
    const streaming = process ? !process.killed : false;

    return {
      device,
      exists,
      streaming,
      mode: streaming ? 'active' : null
    };
  }

  private async createTextImage(text: string): Promise<string> {
    const timestamp = Date.now();
    const outputPath = path.join(this.assetsDir, `text_${timestamp}.jpg`);

    const command = `convert -size 640x480 xc:lightblue -fill black -pointsize 36 -gravity center -draw "text 0,0 '${text}'" ${outputPath}`;
    
    await execAsync(command);
    return outputPath;
  }

  async cleanup(): Promise<void> {
    // Stop all webcam streams
    for (const [device, process] of this.ffmpegProcesses.entries()) {
      process.kill('SIGTERM');
    }
    this.ffmpegProcesses.clear();
  }
}

// Tool schemas for MCP
export const webcamToolSchemas = {
  start_webcam: {
    type: 'object',
    properties: {
      device: { type: 'string', default: '/dev/video20' },
      mode: { 
        type: 'string', 
        enum: ['image', 'video', 'pattern', 'color', 'screen', 'text']
      },
      source: { type: 'string', description: 'Source file, color, pattern, or text' },
      loop: { type: 'boolean', default: true }
    },
    required: ['mode']
  },
  
  stop_webcam: {
    type: 'object',
    properties: {
      device: { type: 'string', default: '/dev/video20' }
    }
  },
  
  capture_webcam_photo: {
    type: 'object',
    properties: {
      device: { type: 'string', default: '/dev/video20' }
    }
  },
  
  webcam_status: {
    type: 'object',
    properties: {
      device: { type: 'string', default: '/dev/video20' }
    }
  },
  
  list_webcams: {
    type: 'object',
    properties: {}
  }
};