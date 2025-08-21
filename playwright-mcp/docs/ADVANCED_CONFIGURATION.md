# Advanced Configuration

Advanced configuration options and customization for MCP Playwright.

## Environment Variables

### Core Settings

```bash
# Node.js environment
NODE_ENV=production|development

# Debug logging
DEBUG=mcp:*           # MCP debug logs
DEBUG=pw:api          # Playwright API logs
DEBUG=pw:browser      # Browser logs

# Headless mode
HEADLESS=true|false

# Default browser
DEFAULT_BROWSER=chromium|firefox|webkit

# Timeouts (milliseconds)
DEFAULT_TIMEOUT=30000
NAVIGATION_TIMEOUT=30000
```

### Browser Configuration

```bash
# Custom browser path
PLAYWRIGHT_BROWSERS_PATH=/custom/path/to/browsers

# Skip browser download
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Specific browser versions
PLAYWRIGHT_CHROMIUM_DOWNLOAD_HOST=https://custom-mirror.com
PLAYWRIGHT_FIREFOX_DOWNLOAD_HOST=https://custom-mirror.com
PLAYWRIGHT_WEBKIT_DOWNLOAD_HOST=https://custom-mirror.com
```

### Network Configuration

```bash
# Proxy settings
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
NO_PROXY=localhost,127.0.0.1

# SSL/TLS
NODE_TLS_REJECT_UNAUTHORIZED=0  # Disable SSL verification (dev only)
NODE_EXTRA_CA_CERTS=/path/to/cert.pem  # Custom CA certificate
```

## MCP Server Configuration

### Custom Server Settings

```javascript
// src/index.ts - Custom configuration
const serverConfig = {
  name: 'mcp-playwright',
  version: '1.0.0',
  capabilities: {
    tools: {},
    resources: {},    // Add resource capabilities
    prompts: {}       // Add prompt capabilities
  },
  options: {
    maxConcurrentBrowsers: 3,
    browserPooling: true,
    cacheTimeout: 300000,  // 5 minutes
    maxRetries: 3
  }
};
```

### Browser Pool Management

```javascript
class BrowserManager {
  private maxBrowsers = parseInt(process.env.MAX_BROWSERS || '3');
  private browserTimeout = parseInt(process.env.BROWSER_TIMEOUT || '300000');
  private pools: Map<string, BrowserPool> = new Map();
  
  async getBrowser(type: string, options: any): Promise<Browser> {
    const pool = this.getPool(type);
    return pool.acquire(options);
  }
  
  private getPool(type: string): BrowserPool {
    if (!this.pools.has(type)) {
      this.pools.set(type, new BrowserPool({
        max: this.maxBrowsers,
        min: 1,
        idleTimeoutMillis: this.browserTimeout,
        createFn: () => this.createBrowser(type),
        destroyFn: (browser) => browser.close()
      }));
    }
    return this.pools.get(type)!;
  }
}
```

### Custom Tool Registration

```javascript
// Add custom tool
server.registerTool({
  name: 'custom_tool',
  description: 'Custom automation tool',
  inputSchema: {
    type: 'object',
    properties: {
      // Define parameters
    }
  },
  handler: async (params) => {
    // Implementation
  }
});
```

## Playwright Configuration

### Advanced playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // Global settings
  globalSetup: './global-setup.ts',
  globalTeardown: './global-teardown.ts',
  
  // Test settings
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: process.env.CI ? 1 : '50%',
  
  // Timeouts
  timeout: 60000,
  expect: {
    timeout: 10000,
    toHaveScreenshot: { maxDiffPixels: 100 }
  },
  
  // Output
  outputDir: './test-results',
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'test-results.json' }],
    ['junit', { outputFile: 'junit.xml' }],
    ['github'],
    ['./custom-reporter.ts']
  ],
  
  // Browser settings
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // Context options
    contextOptions: {
      ignoreHTTPSErrors: true,
      viewport: { width: 1280, height: 720 },
      locale: 'en-US',
      timezoneId: 'America/New_York',
      permissions: ['geolocation', 'notifications'],
      geolocation: { latitude: 40.7128, longitude: -74.0060 },
      colorScheme: 'light',
    },
    
    // Launch options
    launchOptions: {
      slowMo: parseInt(process.env.SLOW_MO || '0'),
      args: ['--disable-dev-shm-usage'],
    }
  },
  
  // Project-specific configurations
  projects: [
    {
      name: 'Desktop Chrome',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: ['--disable-blink-features=AutomationControlled']
        }
      },
    },
    {
      name: 'Mobile Safari',
      use: {
        ...devices['iPhone 12'],
        hasTouch: true,
        isMobile: true,
      },
    },
    {
      name: 'API Testing',
      use: {
        baseURL: process.env.API_URL,
        extraHTTPHeaders: {
          'Authorization': `Bearer ${process.env.API_TOKEN}`,
        },
      },
    },
  ],
  
  // Web server
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    timeout: 120000,
    reuseExistingServer: !process.env.CI,
    env: {
      NODE_ENV: 'test',
    },
  },
});
```

### Custom Browser Contexts

```javascript
// Custom context with authentication
const context = await browser.newContext({
  storageState: 'auth.json',
  httpCredentials: {
    username: 'user',
    password: 'pass'
  },
  proxy: {
    server: 'http://proxy.com:8080',
    bypass: 'localhost'
  }
});

// Save authentication state
await context.storageState({ path: 'auth.json' });
```

## Performance Optimization

### Browser Caching

```javascript
class BrowserCache {
  private cache: Map<string, Browser> = new Map();
  private lastAccess: Map<string, number> = new Map();
  private cleanupInterval = 60000; // 1 minute
  
  constructor() {
    setInterval(() => this.cleanup(), this.cleanupInterval);
  }
  
  async get(key: string, factory: () => Promise<Browser>): Promise<Browser> {
    if (!this.cache.has(key)) {
      this.cache.set(key, await factory());
    }
    this.lastAccess.set(key, Date.now());
    return this.cache.get(key)!;
  }
  
  private cleanup() {
    const now = Date.now();
    const timeout = 300000; // 5 minutes
    
    for (const [key, time] of this.lastAccess.entries()) {
      if (now - time > timeout) {
        this.cache.get(key)?.close();
        this.cache.delete(key);
        this.lastAccess.delete(key);
      }
    }
  }
}
```

### Resource Management

```javascript
// Disable images and CSS for faster loading
await context.route('**/*.{png,jpg,jpeg,gif,svg}', route => route.abort());
await context.route('**/*.css', route => route.abort());

// Cache responses
const cache = new Map();
await context.route('**/*', async route => {
  const url = route.request().url();
  if (cache.has(url)) {
    await route.fulfill({ body: cache.get(url) });
  } else {
    const response = await route.fetch();
    const body = await response.body();
    cache.set(url, body);
    await route.fulfill({ body });
  }
});
```

## Security Configuration

### Sandboxing

```javascript
// Run in sandbox
const browser = await chromium.launch({
  args: [
    '--no-sandbox',  // Disable for Docker
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--no-first-run',
    '--no-zygote',
    '--single-process',  // For Docker
    '--disable-gpu'
  ]
});
```

### Content Security

```javascript
// Set security headers
await context.route('**/*', route => {
  route.continue({
    headers: {
      ...route.request().headers(),
      'X-Frame-Options': 'DENY',
      'X-Content-Type-Options': 'nosniff',
      'X-XSS-Protection': '1; mode=block'
    }
  });
});
```

## Custom Reporters

### Create Custom Reporter

```typescript
// custom-reporter.ts
import { Reporter, TestCase, TestResult } from '@playwright/test/reporter';

class CustomReporter implements Reporter {
  onBegin(config, suite) {
    console.log(`Starting test run with ${suite.allTests().length} tests`);
  }
  
  onTestEnd(test: TestCase, result: TestResult) {
    console.log(`${test.title}: ${result.status}`);
    if (result.status === 'failed') {
      // Send alert or notification
      this.sendAlert(test, result);
    }
  }
  
  onEnd(result) {
    console.log(`Test run finished: ${result.status}`);
    // Generate custom report
    this.generateReport(result);
  }
  
  private sendAlert(test, result) {
    // Implement alerting logic
  }
  
  private generateReport(result) {
    // Implement custom report generation
  }
}

export default CustomReporter;
```

## Scaling Configuration

### Distributed Testing

```javascript
// Configure for distributed testing
const config = {
  // Shard tests across multiple machines
  shard: {
    total: parseInt(process.env.SHARD_TOTAL || '1'),
    current: parseInt(process.env.SHARD_CURRENT || '1')
  },
  
  // Use remote browsers
  use: {
    connectOptions: {
      wsEndpoint: process.env.BROWSER_WS_ENDPOINT
    }
  }
};
```

### Docker Configuration

```dockerfile
# Optimized Dockerfile
FROM mcr.microsoft.com/playwright:v1.48.0-focal

WORKDIR /app

# Copy dependencies first for caching
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Build
RUN npm run build

# Run as non-root user
USER pwuser

# Start server
CMD ["node", "build/index.js"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-playwright
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-playwright
  template:
    metadata:
      labels:
        app: mcp-playwright
    spec:
      containers:
      - name: mcp-playwright
        image: mcp-playwright:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: MAX_BROWSERS
          value: "5"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

## Monitoring & Logging

### Structured Logging

```javascript
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// Use in server
logger.info('Tool executed', { tool: name, duration: ms });
```

### Metrics Collection

```javascript
// Prometheus metrics
import { register, Counter, Histogram } from 'prom-client';

const toolCounter = new Counter({
  name: 'mcp_tool_executions_total',
  help: 'Total number of tool executions',
  labelNames: ['tool', 'status']
});

const toolDuration = new Histogram({
  name: 'mcp_tool_duration_seconds',
  help: 'Tool execution duration',
  labelNames: ['tool']
});

// Track metrics
toolCounter.inc({ tool: 'navigate_to_page', status: 'success' });
toolDuration.observe({ tool: 'navigate_to_page' }, duration);
```

## Extension Development

### Adding New Tools

```javascript
// src/tools/custom-tool.ts
export const customTool = {
  name: 'custom_automation',
  description: 'Custom automation tool',
  inputSchema: {
    type: 'object',
    properties: {
      action: { type: 'string' },
      target: { type: 'string' }
    },
    required: ['action', 'target']
  },
  handler: async (params) => {
    // Implementation
    return {
      content: [{
        type: 'text',
        text: 'Result'
      }]
    };
  }
};

// Register in index.ts
import { customTool } from './tools/custom-tool';
server.registerTool(customTool);
```

### Plugin System

```javascript
// Plugin interface
interface MCPPlugin {
  name: string;
  version: string;
  tools?: Tool[];
  middleware?: Middleware[];
  init?: (server: Server) => void;
}

// Load plugins
const loadPlugins = async (server: Server) => {
  const pluginDir = './plugins';
  const plugins = await fs.readdir(pluginDir);
  
  for (const plugin of plugins) {
    const module = await import(`${pluginDir}/${plugin}`);
    if (module.default?.init) {
      module.default.init(server);
    }
  }
};
```

---

For basic configuration, see [Installation Guide](./INSTALLATION.md).