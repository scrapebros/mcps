# Installation Guide

Complete setup instructions for the MCP Playwright server and Claude integration.

## Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Node.js**: Version 18.0.0 or higher
- **npm**: Version 8.0.0 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Disk Space**: 2GB free space for browsers

### Software Dependencies

1. **Node.js & npm**
   ```bash
   # Check versions
   node --version  # Should be >= 18.0.0
   npm --version   # Should be >= 8.0.0
   ```

2. **Git** (for cloning repository)
   ```bash
   git --version
   ```

3. **Claude Desktop** (for MCP integration)
   - Download from: https://claude.ai/download

## Quick Installation

### One-Command Setup

```bash
# Clone and install
git clone https://github.com/your-org/mcp-playwright.git
cd mcp-playwright
./install.sh
```

This script will:
1. Install Node.js dependencies
2. Build the TypeScript server
3. Install Playwright browsers
4. Configure Claude Desktop

## Manual Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/mcp-playwright.git
cd mcp-playwright
```

### Step 2: Install Dependencies

```bash
# Install Node.js packages
npm install

# Install MCP SDK and Playwright
npm install @modelcontextprotocol/sdk playwright zod
```

### Step 3: Build Server

```bash
# Compile TypeScript to JavaScript
npm run build
```

### Step 4: Install Playwright Browsers

```bash
# Install all browsers
npx playwright install

# Or install specific browsers
npx playwright install chromium
npx playwright install firefox
npx playwright install webkit
```

### Step 5: Install System Dependencies

Some systems require additional dependencies for browsers:

```bash
# Ubuntu/Debian
sudo npx playwright install-deps

# macOS (usually not needed)
# Browsers work out of the box

# Windows
# May need Visual C++ redistributables
```

## Claude Desktop Configuration

### Locate Configuration File

The configuration file location varies by OS:

| OS | Configuration Path |
|----|-------------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

### Configure MCP Server

#### Option 1: Local Installation

```json
{
  "mcpServers": {
    "playwright": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-playwright/build/index.js"]
    }
  }
}
```

#### Option 2: Using npx

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["mcp-playwright"]
    }
  }
}
```

#### Option 3: With Environment Variables

```json
{
  "mcpServers": {
    "playwright": {
      "command": "node",
      "args": ["/path/to/mcp-playwright/build/index.js"],
      "env": {
        "NODE_ENV": "production",
        "DEBUG": "mcp:*",
        "PLAYWRIGHT_BROWSERS_PATH": "/custom/browser/path"
      }
    }
  }
}
```

### Multiple Server Configuration

If you have other MCP servers:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "node",
      "args": ["/path/to/mcp-playwright/build/index.js"]
    },
    "other-server": {
      "command": "node",
      "args": ["/path/to/other-server/index.js"]
    }
  }
}
```

## Python Environment Setup (Optional)

For Python test generation and execution:

### Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Python Dependencies

```txt
playwright==1.48.0
pytest==8.3.3
pytest-playwright==0.5.2
pytest-asyncio==0.24.0
pytest-html==4.1.1
python-dotenv==1.0.1
```

## Verification

### 1. Verify Installation

```bash
# Check build exists
ls -la build/index.js

# Test server directly
node build/index.js
# Should output: "MCP Playwright server started"
# Press Ctrl+C to stop
```

### 2. Test with MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Test server
npx @modelcontextprotocol/inspector node build/index.js
```

### 3. Verify in Claude Desktop

1. Restart Claude Desktop
2. Open Claude
3. Test with: "Use the playwright MCP server to take a screenshot of example.com"

## Platform-Specific Instructions

### macOS

```bash
# Install Xcode Command Line Tools (if needed)
xcode-select --install

# Install browsers
npx playwright install

# Configure Claude
echo '{
  "mcpServers": {
    "playwright": {
      "command": "node",
      "args": ["'$(pwd)'/build/index.js"]
    }
  }
}' > ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install -y curl git

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install browser dependencies
sudo npx playwright install-deps

# Setup MCP Playwright
cd /opt
sudo git clone https://github.com/your-org/mcp-playwright.git
cd mcp-playwright
sudo npm install
sudo npm run build
sudo npx playwright install
```

### Windows

```powershell
# Install Node.js from https://nodejs.org

# Clone repository
git clone https://github.com/your-org/mcp-playwright.git
cd mcp-playwright

# Install dependencies
npm install

# Build server
npm run build

# Install browsers
npx playwright install

# Configure Claude (PowerShell)
$config = @{
  mcpServers = @{
    playwright = @{
      command = "node"
      args = @("C:\path\to\mcp-playwright\build\index.js")
    }
  }
}
$config | ConvertTo-Json | Set-Content "$env:APPDATA\Claude\claude_desktop_config.json"
```

## Docker Installation (Alternative)

### Dockerfile

```dockerfile
FROM node:18-slim

# Install dependencies for browsers
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install Node.js dependencies
RUN npm ci

# Copy source code
COPY . .

# Build server
RUN npm run build

# Install Playwright browsers
RUN npx playwright install chromium

EXPOSE 3000

CMD ["node", "build/index.js"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  mcp-playwright:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DEBUG=mcp:*
    volumes:
      - ./screenshots:/app/screenshots
      - ./reports:/app/reports
```

## Environment Variables

### Optional Configuration

```bash
# Debug mode
export DEBUG=mcp:*

# Custom browser path
export PLAYWRIGHT_BROWSERS_PATH=/custom/path

# Proxy settings
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Headless mode
export HEADLESS=true

# Browser selection
export DEFAULT_BROWSER=chromium
```

## Troubleshooting Installation

### Common Issues

1. **Node.js Version Error**
   ```bash
   # Install Node Version Manager (nvm)
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   nvm install 18
   nvm use 18
   ```

2. **Permission Errors**
   ```bash
   # Fix npm permissions
   mkdir ~/.npm-global
   npm config set prefix '~/.npm-global'
   echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Browser Installation Fails**
   ```bash
   # Install system dependencies
   sudo npx playwright install-deps
   
   # Or manually install browsers to custom location
   PLAYWRIGHT_BROWSERS_PATH=~/playwright-browsers npx playwright install
   ```

4. **Claude Doesn't Recognize Server**
   - Ensure Claude Desktop is fully closed
   - Verify config file syntax (valid JSON)
   - Check absolute paths are correct
   - Restart Claude Desktop

## Updating

### Update MCP Playwright

```bash
cd mcp-playwright
git pull origin main
npm install
npm run build
npx playwright install
```

### Update Claude Configuration

No changes needed unless paths change.

## Uninstallation

### Remove MCP Playwright

```bash
# Remove installation
rm -rf /path/to/mcp-playwright

# Remove from Claude config
# Edit claude_desktop_config.json and remove the "playwright" entry

# Uninstall Playwright browsers (optional)
npx playwright uninstall
```

## Next Steps

1. Verify installation with test command
2. Read [Claude Usage Guide](./CLAUDE_USAGE.md)
3. Explore [MCP Tools Reference](./MCP_TOOLS.md)
4. Check [Troubleshooting Guide](./TROUBLESHOOTING.md) if issues

---

Installation complete! Claude can now use Playwright for web automation.