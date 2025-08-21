# Troubleshooting Guide

Common issues, solutions, and FAQ for MCP Playwright.

## Quick Fixes

| Problem | Solution |
|---------|----------|
| Claude doesn't see server | Restart Claude Desktop |
| Server won't start | Check Node.js version (18+) |
| Browser launch fails | Run `npx playwright install` |
| Permission denied | Check file permissions |
| Timeout errors | Increase timeout values |

## Common Issues

### 1. MCP Server Issues

#### Server Not Starting

**Error:** `Cannot find module '@modelcontextprotocol/sdk'`

**Solution:**
```bash
npm install
npm run build
```

**Error:** `MCP Playwright server started` but Claude doesn't see it

**Solution:**
1. Check Claude configuration file:
```bash
# macOS
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
cat ~/.config/claude/claude_desktop_config.json
```

2. Verify absolute paths:
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

3. Restart Claude Desktop completely (quit and reopen)

#### Permission Errors

**Error:** `EACCES: permission denied`

**Solution:**
```bash
# Fix permissions
chmod +x scripts/*.sh
chmod +x scripts/*.py
chmod 755 build/index.js
```

### 2. Browser Issues

#### Browsers Not Installed

**Error:** `browserType.launch: Executable doesn't exist`

**Solution:**
```bash
# Install all browsers
npx playwright install

# Install specific browser
npx playwright install chromium
npx playwright install firefox
npx playwright install webkit
```

#### System Dependencies Missing

**Error:** `Host system is missing dependencies`

**Solution:**
```bash
# Ubuntu/Debian
sudo npx playwright install-deps

# Or install manually
sudo apt-get update
sudo apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libxss1 libasound2
```

#### Browser Launch Timeout

**Error:** `browserType.launch: Timeout 30000ms exceeded`

**Solution:**
1. Increase timeout:
```javascript
const browser = await chromium.launch({
  timeout: 60000 // 60 seconds
});
```

2. Check system resources:
```bash
# Check available memory
free -h

# Check CPU usage
top
```

### 3. Claude Integration Issues

#### Claude Can't Find Tools

**Problem:** Claude says "I don't have access to playwright tools"

**Solution:**
1. Verify server is in config:
```bash
# Check if playwright server is configured
grep -A3 "playwright" ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. Test server directly:
```bash
node /opt/mcp-playwright/build/index.js
# Should output: "MCP Playwright server started"
```

3. Use MCP Inspector:
```bash
npx @modelcontextprotocol/inspector node build/index.js
```

#### Tools Not Executing

**Problem:** Claude acknowledges tools but execution fails

**Solution:**
1. Check error logs in Claude
2. Verify tool parameters are correct
3. Test tool directly with inspector

### 4. Network Issues

#### Proxy Configuration

**Problem:** Behind corporate proxy

**Solution:**
```bash
# Set proxy environment variables
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
export NO_PROXY=localhost,127.0.0.1

# Or in Claude config
{
  "mcpServers": {
    "playwright": {
      "command": "node",
      "args": ["build/index.js"],
      "env": {
        "HTTP_PROXY": "http://proxy.example.com:8080",
        "HTTPS_PROXY": "http://proxy.example.com:8080"
      }
    }
  }
}
```

#### SSL Certificate Errors

**Error:** `Error: self signed certificate`

**Solution:**
```bash
# Temporary fix (not recommended for production)
export NODE_TLS_REJECT_UNAUTHORIZED=0

# Better solution: Add certificate
export NODE_EXTRA_CA_CERTS=/path/to/certificate.pem
```

### 5. Performance Issues

#### Slow Execution

**Problem:** Tools take too long to execute

**Solutions:**
1. Use headless mode:
```json
{
  "headless": true
}
```

2. Reduce viewport size:
```javascript
await page.setViewportSize({ width: 1280, height: 720 });
```

3. Disable images:
```javascript
await context.route('**/*.{png,jpg,jpeg}', route => route.abort());
```

#### Memory Leaks

**Problem:** Memory usage increases over time

**Solution:**
1. Ensure browsers are closed:
```javascript
try {
  // Your code
} finally {
  await browser.close();
}
```

2. Clear cache periodically:
```javascript
await context.clearCookies();
await context.clearPermissions();
```

### 6. Testing Issues

#### Tests Failing Randomly

**Problem:** Flaky tests

**Solutions:**
1. Add explicit waits:
```javascript
await page.waitForSelector('.element');
await page.waitForLoadState('networkidle');
```

2. Increase timeouts:
```javascript
test.setTimeout(60000);
```

3. Add retry logic:
```javascript
test.describe('tests', () => {
  test.describe.configure({ retries: 2 });
  // tests
});
```

#### Screenshot Issues

**Problem:** Screenshots not saving

**Solution:**
1. Check directory exists:
```bash
mkdir -p reports/screenshots
```

2. Verify permissions:
```bash
chmod 755 reports/screenshots
```

3. Check disk space:
```bash
df -h
```

### 7. Python Environment Issues

#### Virtual Environment Not Working

**Error:** `No module named 'playwright'`

**Solution:**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

#### Python Version Mismatch

**Error:** `Python 3.8+ required`

**Solution:**
```bash
# Check Python version
python3 --version

# Install Python 3.8+
# Ubuntu/Debian
sudo apt-get install python3.8

# macOS
brew install python@3.8
```

## FAQ

### General Questions

**Q: Can I use this without Claude Desktop?**
A: Yes, the MCP server can be used with any MCP-compatible client.

**Q: Which browsers are supported?**
A: Chromium (Chrome, Edge), Firefox, and WebKit (Safari).

**Q: Can I run tests in parallel?**
A: Yes, use `--workers` flag or configure in playwright.config.ts.

**Q: How do I update Playwright?**
A: Run `npm update playwright` and `npx playwright install`.

### Claude-Specific Questions

**Q: Why doesn't Claude see the MCP server after installation?**
A: Claude Desktop must be completely restarted (quit and reopen).

**Q: Can Claude run tests automatically on a schedule?**
A: Not directly, but you can set up cron jobs that Claude can trigger.

**Q: What's the maximum timeout for tool execution?**
A: Default is 30 seconds, configurable up to several minutes.

### Technical Questions

**Q: Can I use custom browsers?**
A: Yes, specify executable path in launch options.

**Q: How do I debug failing tests?**
A: Use `--debug` flag or `PWDEBUG=1` environment variable.

**Q: Can I test local/localhost sites?**
A: Yes, ensure the local server is running.

**Q: How do I test authenticated pages?**
A: Use context with saved authentication state.

## Error Messages Reference

### Node.js Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| `MODULE_NOT_FOUND` | Missing dependency | Run `npm install` |
| `ENOENT` | File not found | Check file paths |
| `EACCES` | Permission denied | Fix permissions |
| `EADDRINUSE` | Port in use | Change port or kill process |

### Playwright Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| `Target closed` | Page/browser closed | Check for early close |
| `Timeout exceeded` | Operation too slow | Increase timeout |
| `Element not found` | Selector failed | Verify selector |
| `Navigation failed` | Page didn't load | Check URL/network |

### MCP Errors

| Error | Meaning | Solution |
|-------|---------|----------|
| `Invalid params` | Wrong parameters | Check tool schema |
| `Method not found` | Unknown tool | Verify tool name |
| `Internal error` | Server error | Check logs |

## Debug Commands

### Check System

```bash
# Node version
node --version

# NPM version
npm --version

# Python version
python3 --version

# Playwright version
npx playwright --version

# Check browsers
npx playwright install --list
```

### Test Connectivity

```bash
# Test MCP server
echo '{"jsonrpc":"2.0","method":"list_tools","id":1}' | node build/index.js

# Test browser launch
npx playwright test tests/e2e/js/example.spec.ts --headed

# Test Python
python3 -c "from playwright.sync_api import sync_playwright; print('OK')"
```

### Clean and Rebuild

```bash
# Clean build
rm -rf build node_modules

# Reinstall and rebuild
npm install
npm run build

# Clean Python
rm -rf venv __pycache__ .pytest_cache

# Reinstall Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Getting Help

### Logs and Debugging

1. Enable debug logging:
```bash
export DEBUG=mcp:*
export DEBUG=pw:api
```

2. Check Claude logs:
- macOS: `~/Library/Logs/Claude/`
- Linux: `~/.config/claude/logs/`

3. Use verbose mode:
```bash
npm test -- --verbose
pytest -vv
```

### Support Resources

- Check this troubleshooting guide
- Review [Installation Guide](./INSTALLATION.md)
- See [Testing Guide](./TESTING.md)
- Consult [MCP Tools Reference](./MCP_TOOLS.md)

---

If issues persist, check the latest documentation or file an issue in the project repository.