#!/usr/bin/env node

/**
 * MCP Server for Playwright Web Testing and Automation
 * Provides tools for web testing, scraping, and automation through MCP
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { chromium, firefox, webkit, Browser, Page, BrowserContext } from 'playwright';
import { z } from 'zod';
import * as fs from 'fs/promises';
import * as path from 'path';
import { WebcamManager, webcamToolSchemas } from './webcam-tools.js';

// Tool parameter schemas
const NavigateSchema = z.object({
  url: z.string().url().describe('The URL to navigate to'),
  browser: z.enum(['chromium', 'firefox', 'webkit']).optional().default('chromium'),
  headless: z.boolean().optional().default(true),
  waitUntil: z.enum(['load', 'domcontentloaded', 'networkidle']).optional().default('networkidle'),
});

const ScreenshotSchema = z.object({
  url: z.string().url().describe('The URL to capture'),
  path: z.string().optional().describe('Path to save the screenshot'),
  fullPage: z.boolean().optional().default(true),
  browser: z.enum(['chromium', 'firefox', 'webkit']).optional().default('chromium'),
  headless: z.boolean().optional().default(true),
});

const ExtractDataSchema = z.object({
  url: z.string().url().describe('The URL to extract data from'),
  selectors: z.record(z.string()).describe('Object mapping field names to CSS selectors'),
  browser: z.enum(['chromium', 'firefox', 'webkit']).optional().default('chromium'),
  headless: z.boolean().optional().default(true),
});

const FillFormSchema = z.object({
  url: z.string().url().describe('The URL with the form'),
  formData: z.record(z.any()).describe('Object with form field names and values'),
  submitSelector: z.string().optional().default('button[type="submit"]'),
  browser: z.enum(['chromium', 'firefox', 'webkit']).optional().default('chromium'),
  headless: z.boolean().optional().default(true),
});

const TestWebsiteSchema = z.object({
  url: z.string().url().describe('The URL to test'),
  tests: z.array(z.enum([
    'performance',
    'accessibility',
    'seo',
    'responsiveness',
    'links',
    'console-errors'
  ])).optional().default(['performance', 'accessibility', 'console-errors']),
  browser: z.enum(['chromium', 'firefox', 'webkit']).optional().default('chromium'),
  headless: z.boolean().optional().default(true),
});

const RunScriptSchema = z.object({
  url: z.string().url().describe('The URL to run the script on'),
  script: z.string().describe('JavaScript code to execute on the page'),
  browser: z.enum(['chromium', 'firefox', 'webkit']).optional().default('chromium'),
  headless: z.boolean().optional().default(true),
});

const GenerateTestSchema = z.object({
  url: z.string().url().describe('The URL to generate tests for'),
  type: z.enum([
    'e2e',
    'form',
    'navigation',
    'api',
    'visual',
    'performance',
    'accessibility'
  ]).describe('Type of test to generate'),
  language: z.enum(['javascript', 'typescript', 'python']).optional().default('typescript'),
});

// Browser management
class BrowserManager {
  private browsers: Map<string, Browser> = new Map();

  async getBrowser(type: 'chromium' | 'firefox' | 'webkit', headless: boolean = true): Promise<Browser> {
    const key = `${type}-${headless}`;
    
    if (!this.browsers.has(key)) {
      let browser: Browser;
      switch (type) {
        case 'firefox':
          browser = await firefox.launch({ headless });
          break;
        case 'webkit':
          browser = await webkit.launch({ headless });
          break;
        default:
          browser = await chromium.launch({ headless });
      }
      this.browsers.set(key, browser);
    }
    
    return this.browsers.get(key)!;
  }

  async cleanup() {
    for (const browser of this.browsers.values()) {
      await browser.close();
    }
    this.browsers.clear();
  }
}

// Create server instance
const server = new Server(
  {
    name: 'mcp-playwright',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const browserManager = new BrowserManager();
const webcamManager = new WebcamManager();

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'navigate_to_page',
        description: 'Navigate to a URL and get page information',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'The URL to navigate to' },
            browser: { type: 'string', enum: ['chromium', 'firefox', 'webkit'], default: 'chromium' },
            headless: { type: 'boolean', default: true },
            waitUntil: { type: 'string', enum: ['load', 'domcontentloaded', 'networkidle'], default: 'networkidle' },
          },
          required: ['url'],
        },
      },
      {
        name: 'take_screenshot',
        description: 'Take a screenshot of a webpage',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'The URL to capture' },
            path: { type: 'string', description: 'Path to save the screenshot' },
            fullPage: { type: 'boolean', default: true },
            browser: { type: 'string', enum: ['chromium', 'firefox', 'webkit'], default: 'chromium' },
            headless: { type: 'boolean', default: true },
          },
          required: ['url'],
        },
      },
      {
        name: 'extract_data',
        description: 'Extract data from a webpage using CSS selectors',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'The URL to extract data from' },
            selectors: { type: 'object', description: 'Object mapping field names to CSS selectors' },
            browser: { type: 'string', enum: ['chromium', 'firefox', 'webkit'], default: 'chromium' },
            headless: { type: 'boolean', default: true },
          },
          required: ['url', 'selectors'],
        },
      },
      {
        name: 'fill_form',
        description: 'Fill and submit a form on a webpage',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'The URL with the form' },
            formData: { type: 'object', description: 'Object with form field names and values' },
            submitSelector: { type: 'string', default: 'button[type="submit"]' },
            browser: { type: 'string', enum: ['chromium', 'firefox', 'webkit'], default: 'chromium' },
            headless: { type: 'boolean', default: true },
          },
          required: ['url', 'formData'],
        },
      },
      {
        name: 'test_website',
        description: 'Run automated tests on a website (performance, accessibility, etc.)',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'The URL to test' },
            tests: {
              type: 'array',
              items: {
                type: 'string',
                enum: ['performance', 'accessibility', 'seo', 'responsiveness', 'links', 'console-errors']
              },
              default: ['performance', 'accessibility', 'console-errors']
            },
            browser: { type: 'string', enum: ['chromium', 'firefox', 'webkit'], default: 'chromium' },
            headless: { type: 'boolean', default: true },
          },
          required: ['url'],
        },
      },
      {
        name: 'run_script',
        description: 'Execute JavaScript code on a webpage',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'The URL to run the script on' },
            script: { type: 'string', description: 'JavaScript code to execute' },
            browser: { type: 'string', enum: ['chromium', 'firefox', 'webkit'], default: 'chromium' },
            headless: { type: 'boolean', default: true },
          },
          required: ['url', 'script'],
        },
      },
      {
        name: 'generate_test',
        description: 'Generate test code for a webpage',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'The URL to generate tests for' },
            type: {
              type: 'string',
              enum: ['e2e', 'form', 'navigation', 'api', 'visual', 'performance', 'accessibility'],
              description: 'Type of test to generate'
            },
            language: {
              type: 'string',
              enum: ['javascript', 'typescript', 'python'],
              default: 'typescript'
            },
          },
          required: ['url', 'type'],
        },
      },
      {
        name: 'start_webcam',
        description: 'Start a fake webcam with image, video, or pattern',
        inputSchema: webcamToolSchemas.start_webcam,
      },
      {
        name: 'stop_webcam',
        description: 'Stop the fake webcam stream',
        inputSchema: webcamToolSchemas.stop_webcam,
      },
      {
        name: 'capture_webcam_photo',
        description: 'Capture a photo from the webcam',
        inputSchema: webcamToolSchemas.capture_webcam_photo,
      },
      {
        name: 'webcam_status',
        description: 'Get current webcam status',
        inputSchema: webcamToolSchemas.webcam_status,
      },
      {
        name: 'list_webcams',
        description: 'List available webcam devices',
        inputSchema: webcamToolSchemas.list_webcams,
      },
    ],
  };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args } = request.params;

    switch (name) {
      case 'navigate_to_page': {
        const params = NavigateSchema.parse(args);
        const browser = await browserManager.getBrowser(params.browser, params.headless);
        const context = await browser.newContext();
        const page = await context.newPage();

        const response = await page.goto(params.url, {
          waitUntil: params.waitUntil as any,
        });

        const pageInfo = {
          url: page.url(),
          title: await page.title(),
          status: response?.status(),
          headers: response?.headers(),
          content: await page.content(),
        };

        await context.close();

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(pageInfo, null, 2),
            },
          ],
        };
      }

      case 'take_screenshot': {
        const params = ScreenshotSchema.parse(args);
        const browser = await browserManager.getBrowser(params.browser, params.headless);
        const context = await browser.newContext();
        const page = await context.newPage();

        await page.goto(params.url, { waitUntil: 'networkidle' });

        const screenshotPath = params.path || `screenshot-${Date.now()}.png`;
        const screenshotBuffer = await page.screenshot({
          path: screenshotPath,
          fullPage: params.fullPage,
        });

        await context.close();

        return {
          content: [
            {
              type: 'text',
              text: `Screenshot saved to: ${screenshotPath}`,
            },
            {
              type: 'image',
              data: screenshotBuffer.toString('base64'),
              mimeType: 'image/png',
            },
          ],
        };
      }

      case 'extract_data': {
        const params = ExtractDataSchema.parse(args);
        const browser = await browserManager.getBrowser(params.browser, params.headless);
        const context = await browser.newContext();
        const page = await context.newPage();

        await page.goto(params.url, { waitUntil: 'networkidle' });

        const extractedData: Record<string, any> = {};

        for (const [fieldName, selector] of Object.entries(params.selectors)) {
          try {
            const elements = await page.$$(selector);
            if (elements.length === 0) {
              extractedData[fieldName] = null;
            } else if (elements.length === 1) {
              extractedData[fieldName] = await elements[0].textContent();
            } else {
              extractedData[fieldName] = await Promise.all(
                elements.map(el => el.textContent())
              );
            }
          } catch (error) {
            extractedData[fieldName] = `Error: ${error}`;
          }
        }

        await context.close();

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(extractedData, null, 2),
            },
          ],
        };
      }

      case 'fill_form': {
        const params = FillFormSchema.parse(args);
        const browser = await browserManager.getBrowser(params.browser, params.headless);
        const context = await browser.newContext();
        const page = await context.newPage();

        await page.goto(params.url, { waitUntil: 'networkidle' });

        // Fill form fields
        for (const [fieldName, value] of Object.entries(params.formData)) {
          const selectors = [
            `input[name="${fieldName}"]`,
            `input[id="${fieldName}"]`,
            `textarea[name="${fieldName}"]`,
            `select[name="${fieldName}"]`,
            `[data-testid="${fieldName}"]`,
          ];

          let filled = false;
          for (const selector of selectors) {
            try {
              const element = await page.$(selector);
              if (element) {
                const tagName = await element.evaluate(el => el.tagName.toLowerCase());
                
                if (tagName === 'select') {
                  await page.selectOption(selector, value as string);
                } else if (tagName === 'input') {
                  const type = await element.getAttribute('type');
                  if (type === 'checkbox' || type === 'radio') {
                    if (value) await element.check();
                  } else {
                    await element.fill(String(value));
                  }
                } else {
                  await element.fill(String(value));
                }
                filled = true;
                break;
              }
            } catch (error) {
              // Try next selector
            }
          }
        }

        // Submit form
        try {
          await page.click(params.submitSelector);
          await page.waitForLoadState('networkidle');
        } catch (error) {
          // Form might submit via JavaScript
        }

        const result = {
          url: page.url(),
          title: await page.title(),
          success: true,
        };

        await context.close();

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'test_website': {
        const params = TestWebsiteSchema.parse(args);
        const browser = await browserManager.getBrowser(params.browser, params.headless);
        const context = await browser.newContext();
        const page = await context.newPage();

        const results: Record<string, any> = {
          url: params.url,
          tests: {},
        };

        // Console error tracking
        const consoleErrors: string[] = [];
        if (params.tests.includes('console-errors')) {
          page.on('console', msg => {
            if (msg.type() === 'error') {
              consoleErrors.push(msg.text());
            }
          });
        }

        await page.goto(params.url, { waitUntil: 'networkidle' });

        // Performance test
        if (params.tests.includes('performance')) {
          const metrics = await page.evaluate(() => {
            const timing = performance.timing;
            return {
              loadTime: timing.loadEventEnd - timing.navigationStart,
              domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
              firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
            };
          });
          results.tests.performance = metrics;
        }

        // Accessibility test (basic)
        if (params.tests.includes('accessibility')) {
          const accessibilityIssues = await page.evaluate(() => {
            const issues = [];
            
            // Check for alt text on images
            const images = document.querySelectorAll('img');
            images.forEach((img, index) => {
              if (!img.hasAttribute('alt')) {
                issues.push(`Image ${index + 1} missing alt text`);
              }
            });

            // Check for form labels
            const inputs = document.querySelectorAll('input, textarea, select');
            inputs.forEach((input: any, index) => {
              const id = input.id;
              if (id) {
                const label = document.querySelector(`label[for="${id}"]`);
                if (!label && input.parentElement?.tagName !== 'LABEL') {
                  issues.push(`Input ${index + 1} missing label`);
                }
              }
            });

            return issues;
          });
          results.tests.accessibility = accessibilityIssues;
        }

        // SEO test (basic)
        if (params.tests.includes('seo')) {
          const seoData = await page.evaluate(() => {
            const data: Record<string, any> = {};
            
            // Check meta tags
            const title = document.querySelector('title');
            data.title = title ? title.textContent : 'Missing';
            
            const description = document.querySelector('meta[name="description"]');
            data.description = description ? description.getAttribute('content') : 'Missing';
            
            // Check headings
            data.h1Count = document.querySelectorAll('h1').length;
            
            return data;
          });
          results.tests.seo = seoData;
        }

        // Responsive test
        if (params.tests.includes('responsiveness')) {
          const viewports = [
            { width: 1920, height: 1080, name: 'desktop' },
            { width: 768, height: 1024, name: 'tablet' },
            { width: 375, height: 667, name: 'mobile' },
          ];

          const responsiveResults = [];
          for (const viewport of viewports) {
            await page.setViewportSize(viewport);
            await page.waitForTimeout(500);
            
            const isResponsive = await page.evaluate(() => {
              return document.body.scrollWidth <= window.innerWidth;
            });

            responsiveResults.push({
              viewport: viewport.name,
              isResponsive,
            });
          }
          results.tests.responsiveness = responsiveResults;
        }

        // Link checking
        if (params.tests.includes('links')) {
          const links = await page.evaluate(() => {
            const allLinks = Array.from(document.querySelectorAll('a[href]'));
            return allLinks.map(link => ({
              text: link.textContent?.trim(),
              href: link.getAttribute('href'),
            }));
          });
          results.tests.links = links.slice(0, 20); // Limit to first 20 links
        }

        // Console errors
        if (params.tests.includes('console-errors')) {
          results.tests.consoleErrors = consoleErrors;
        }

        await context.close();

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(results, null, 2),
            },
          ],
        };
      }

      case 'run_script': {
        const params = RunScriptSchema.parse(args);
        const browser = await browserManager.getBrowser(params.browser, params.headless);
        const context = await browser.newContext();
        const page = await context.newPage();

        await page.goto(params.url, { waitUntil: 'networkidle' });

        const result = await page.evaluate(params.script);

        await context.close();

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'generate_test': {
        const params = GenerateTestSchema.parse(args);
        
        // Generate test code based on type and language
        let testCode = '';
        
        if (params.language === 'python') {
          testCode = generatePythonTest(params.url, params.type);
        } else {
          testCode = generateJavaScriptTest(params.url, params.type, params.language === 'typescript');
        }

        return {
          content: [
            {
              type: 'text',
              text: testCode,
            },
          ],
        };
      }

      case 'start_webcam': {
        const params = args as any;
        const result = await webcamManager.startWebcam(params);
        
        return {
          content: [
            {
              type: 'text',
              text: result.success 
                ? `${result.message}\nDevice: ${result.data?.device}\nMode: ${result.data?.mode}\nSource: ${result.data?.source || 'default'}`
                : `Failed to start webcam: ${result.error}`,
            },
          ],
        };
      }

      case 'stop_webcam': {
        const params = args as any;
        const device = params.device || '/dev/video20';
        webcamManager.stopWebcam(device);
        
        return {
          content: [
            {
              type: 'text',
              text: `Webcam stopped on ${device}`,
            },
          ],
        };
      }

      case 'capture_webcam_photo': {
        const params = args as any;
        const result = await webcamManager.capturePhoto(params.device);
        
        if (result.success) {
          return {
            content: [
              {
                type: 'text',
                text: `Photo captured successfully\nPath: ${result.data?.path}\nDevice: ${result.data?.device}`,
              },
              {
                type: 'image',
                data: result.data?.base64,
                mimeType: 'image/jpeg',
              },
            ],
          };
        } else {
          return {
            content: [
              {
                type: 'text',
                text: `Failed to capture photo: ${result.error}`,
              },
            ],
          };
        }
      }

      case 'webcam_status': {
        const params = args as any;
        const status = await webcamManager.getStatus(params.device);
        
        return {
          content: [
            {
              type: 'text',
              text: `Webcam Status:\nDevice: ${status.device}\nExists: ${status.exists}\nStreaming: ${status.streaming}\nMode: ${status.mode || 'none'}`,
            },
          ],
        };
      }

      case 'list_webcams': {
        const devices = await webcamManager.listDevices();
        
        return {
          content: [
            {
              type: 'text',
              text: devices.length > 0 
                ? `Available webcam devices:\n${devices.join('\n')}`
                : 'No webcam devices found',
            },
          ],
        };
      }

      default:
        throw new McpError(
          ErrorCode.MethodNotFound,
          `Unknown tool: ${name}`
        );
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new McpError(
        ErrorCode.InvalidParams,
        `Invalid parameters: ${error.errors.map(e => `${e.path.join('.')}: ${e.message}`).join(', ')}`
      );
    }
    throw error;
  }
});

// Test generation functions
function generateJavaScriptTest(url: string, type: string, isTypeScript: boolean): string {
  const ext = isTypeScript ? 'ts' : 'js';
  const imports = isTypeScript
    ? "import { test, expect } from '@playwright/test';"
    : "const { test, expect } = require('@playwright/test');";

  const baseTest = `${imports}

test.describe('${type} tests for ${url}', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('${url}');
  });

`;

  switch (type) {
    case 'e2e':
      return baseTest + `  test('complete user journey', async ({ page }) => {
    // Navigate through the site
    await expect(page).toHaveTitle(/.*/)
    
    // Click first navigation link
    const navLink = page.locator('nav a').first();
    if (await navLink.isVisible()) {
      await navLink.click();
      await page.waitForLoadState('networkidle');
    }
    
    // Verify page loaded
    await expect(page.locator('body')).toBeVisible();
  });
});`;

    case 'form':
      return baseTest + `  test('form submission', async ({ page }) => {
    // Fill form fields
    await page.fill('input[type="text"]', 'Test User');
    await page.fill('input[type="email"]', 'test@example.com');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for response
    await page.waitForLoadState('networkidle');
    
    // Check for success message
    const success = page.locator('.success, .alert-success');
    await expect(success).toBeVisible();
  });
});`;

    case 'performance':
      return baseTest + `  test('performance metrics', async ({ page }) => {
    const metrics = await page.evaluate(() => {
      const timing = performance.timing;
      return {
        loadTime: timing.loadEventEnd - timing.navigationStart,
        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
      };
    });
    
    expect(metrics.loadTime).toBeLessThan(3000);
    expect(metrics.domContentLoaded).toBeLessThan(1500);
  });
});`;

    default:
      return baseTest + `  test('basic test', async ({ page }) => {
    await expect(page).toHaveTitle(/.*/)
    await expect(page.locator('body')).toBeVisible();
  });
});`;
  }
}

function generatePythonTest(url: string, type: string): string {
  const baseTest = `import pytest
from playwright.sync_api import Page, expect

class Test${type.charAt(0).toUpperCase() + type.slice(1)}:
    def test_${type}_${url.replace(/[^a-z0-9]/gi, '_')}(self, page: Page):
        page.goto("${url}")
        
`;

  switch (type) {
    case 'e2e':
      return baseTest + `        # Complete user journey
        expect(page).to_have_title(re.compile(".*"))
        
        # Navigate through site
        nav_link = page.locator("nav a").first
        if nav_link.is_visible():
            nav_link.click()
            page.wait_for_load_state("networkidle")
        
        # Verify page loaded
        expect(page.locator("body")).to_be_visible()`;

    case 'form':
      return baseTest + `        # Fill and submit form
        page.fill('input[type="text"]', "Test User")
        page.fill('input[type="email"]', "test@example.com")
        
        # Submit
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        
        # Check success
        success = page.locator(".success, .alert-success")
        expect(success).to_be_visible()`;

    default:
      return baseTest + `        # Basic test
        expect(page).to_have_title(re.compile(".*"))
        expect(page.locator("body")).to_be_visible()`;
  }
}

// Cleanup on shutdown
process.on('SIGINT', async () => {
  await browserManager.cleanup();
  await webcamManager.cleanup();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  await browserManager.cleanup();
  await webcamManager.cleanup();
  process.exit(0);
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP Playwright server started');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});