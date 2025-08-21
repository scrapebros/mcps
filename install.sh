#!/bin/bash

# MCP Playwright Server Installation Script

set -e

echo "🚀 Installing MCP Playwright Server..."
echo ""

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 18+ is required. Current version: $(node -v)"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build TypeScript
echo "🔨 Building server..."
npm run build

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
npx playwright install

# Create config directory if it doesn't exist
CONFIG_DIR="$HOME/.config/claude"
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
fi

# Detect OS and set config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CONFIG_PATH="$HOME/.config/claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows
    CONFIG_PATH="$APPDATA/Claude/claude_desktop_config.json"
else
    CONFIG_PATH="$HOME/.config/claude/claude_desktop_config.json"
fi

# Create config directory if needed
CONFIG_DIR=$(dirname "$CONFIG_PATH")
mkdir -p "$CONFIG_DIR"

# Get absolute path to this installation
INSTALL_PATH=$(pwd)

# Check if config exists
if [ -f "$CONFIG_PATH" ]; then
    echo ""
    echo "📝 Existing Claude configuration found."
    echo "Add this to your $CONFIG_PATH:"
    echo ""
    cat << EOF
{
  "mcpServers": {
    "playwright": {
      "command": "node",
      "args": ["$INSTALL_PATH/build/index.js"]
    }
  }
}
EOF
else
    # Create new config
    cat > "$CONFIG_PATH" << EOF
{
  "mcpServers": {
    "playwright": {
      "command": "node",
      "args": ["$INSTALL_PATH/build/index.js"]
    }
  }
}
EOF
    echo "✅ Created Claude configuration at: $CONFIG_PATH"
fi

echo ""
echo "✨ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Restart Claude Desktop to load the MCP server"
echo "2. Test by asking Claude: 'Use the playwright MCP server to take a screenshot of example.com'"
echo ""
echo "📚 Available tools:"
echo "  - navigate_to_page: Navigate to URLs and get page info"
echo "  - take_screenshot: Capture webpage screenshots"
echo "  - extract_data: Extract data using CSS selectors"
echo "  - fill_form: Fill and submit forms"
echo "  - test_website: Run automated tests"
echo "  - run_script: Execute JavaScript on pages"
echo "  - generate_test: Generate test code"
echo ""
echo "For more information, see README_MCP.md"