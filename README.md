# MCP Servers Collection

A collection of Model Context Protocol (MCP) servers for Claude Code integration.

## Available MCPs

### 1. JoyCaption MCP
**Purpose**: Generate uncensored, detailed image captions for AI training datasets

**Features**:
- Multiple caption modes (training, detailed_uncensored, descriptive, etc.)
- Avatar name support for character-specific datasets
- Batch processing with progress tracking
- JSON metadata export alongside images
- Skip existing captions to avoid reprocessing

**Location**: `joycaption-mcp/`

### 2. Domain Checker MCP
**Purpose**: Check domain availability for branding/business purposes

**Features**:
- Two-stage verification (DNS lookup → WHOIS query)
- 24-hour result caching to reduce redundant lookups
- Round-robin WHOIS server distribution
- Batch checking capabilities
- Clean categorized output (available/unavailable/errors)

**Location**: `domain-checker/`

## Quick Start

### Installation
Each MCP can be installed independently:

```bash
# JoyCaption MCP
cd joycaption-mcp
pip install -e .

# Domain Checker MCP  
cd domain-checker
pip install -e .
```

### Claude Code Configuration
Add to your Claude Code configuration:

```json
{
  "mcpServers": {
    "joycaption": {
      "command": "python",
      "args": ["-m", "joycaption_mcp"],
      "cwd": "/path/to/joycaption-mcp"
    },
    "domain-checker": {
      "command": "python", 
      "args": ["-m", "domain_checker_mcp"],
      "cwd": "/path/to/domain-checker"
    }
  }
}
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:
- `docs/CLAUDE.md` - Main project context and architecture
- `docs/UPDATES.md` - Change log
- `docs/joycaption-mcp/` - JoyCaption specific documentation
- `docs/domain-checker/` - Domain checker specific documentation

## Requirements

- Python 3.10+
- Claude Code MCP support
- See individual MCP directories for specific dependencies

## License

Individual MCPs may have their own licensing. See each directory for details.