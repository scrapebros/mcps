# MCP Playwright Server

A Model Context Protocol (MCP) server that provides Playwright browser automation tools for Claude Desktop.

## Features

- 🌐 **Browser Automation**: Control Chromium, Firefox, and WebKit browsers
- 📸 **Screenshot Capture**: Take full-page or element-specific screenshots  
- 🎥 **Webcam Simulation**: Test video applications with fake webcam feeds
- 🧪 **Web Testing**: Automated testing for performance, accessibility, and functionality
- 📝 **Test Generation**: Generate test code in JavaScript, TypeScript, or Python
- 🎭 **Multi-Browser Support**: Test across different browser engines

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/scrapebros/mcps.git
cd mcp-playwright

# Install dependencies
npm install
npm run build

# For Python support
pip install -r requirements.txt
```

### Configure Claude Desktop

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "playwright": {
      "command": "node",
      "args": ["/path/to/mcp-playwright/build/index.js"]
    }
  }
}
```

## Available Tools

### Core Tools

- `navigate_to_page` - Navigate to a URL and get page information
- `take_screenshot` - Capture screenshots of web pages
- `extract_data` - Extract data using CSS selectors
- `fill_form` - Fill and submit forms automatically
- `test_website` - Run automated tests (performance, accessibility, etc.)
- `run_script` - Execute JavaScript on pages
- `generate_test` - Generate test code for web pages

### Webcam Tools

- `start_webcam` - Start fake webcam with various modes
- `stop_webcam` - Stop webcam stream
- `capture_webcam_photo` - Capture photos from webcam
- `webcam_status` - Check webcam status
- `list_webcams` - List available webcam devices

## Examples

### Basic Web Automation

```javascript
// Navigate and screenshot
await navigate_to_page({ url: "https://example.com" });
await take_screenshot({ url: "https://example.com", fullPage: true });
```

### Webcam Testing

```javascript
// Start fake webcam with test pattern
await start_webcam({ 
  mode: "pattern", 
  source: "smpte" 
});

// Use custom image as webcam
await start_webcam({ 
  mode: "image", 
  source: "/path/to/image.jpg" 
});
```

### Form Automation

```javascript
await fill_form({
  url: "https://example.com/form",
  formData: {
    name: "John Doe",
    email: "john@example.com"
  }
});
```

## Project Structure

```
mcp-playwright/
├── src/                 # TypeScript source files
│   ├── index.ts        # Main MCP server
│   └── webcam-tools.ts # Webcam functionality
├── scripts/            # Python automation scripts
├── tests/              # Test files
├── docs/               # Documentation
└── webcam-assets/      # Webcam test assets
```

## Requirements

- Node.js 18+
- Python 3.8+ (for Python scripts)
- FFmpeg (for webcam features)
- ImageMagick (for image processing)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the GitHub issues page.