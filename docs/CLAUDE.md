# CLAUDE.md - MCP Servers Project Documentation

This document provides comprehensive context for the MCP (Model Context Protocol) servers project, designed to maintain continuity across development sessions.

## Project Overview

This project contains two functional MCP servers that integrate with Claude Code:
1. **JoyCaption MCP** - AI-powered image captioning for fine-tuning datasets
2. **Domain Checker MCP** - Domain availability checking with caching

Both servers demonstrate different aspects of MCP integration and serve practical purposes for AI model training and domain research.

## Architecture

### Directory Structure
```
/opt/mcps/
├── docs/                        # All documentation
│   ├── CLAUDE.md               # This file - project context
│   ├── UPDATES.md              # Chronological change log
│   ├── domain-checker/         # Domain checker specific docs
│   └── joycaption-mcp/         # JoyCaption specific docs
├── domain-checker/              # Domain availability checker MCP
│   ├── domain_checker_mcp/     # Python package
│   ├── pyproject.toml          # Package configuration
│   ├── mcp.json                # MCP configuration
│   └── README.md               # Server documentation
├── joycaption-mcp/             # Image captioning MCP
│   ├── joycaption_mcp/         # Python package
│   ├── batch_caption*.py       # Batch processing scripts
│   ├── samples/                # Test images
│   └── requirements.txt        # Dependencies
└── old/                        # Archived files
    ├── deprecated/             # Old versions of scripts
    ├── output/                 # Previous run outputs
    └── tests/                  # Old test files
```

### Key Components

#### 1. JoyCaption MCP (`/opt/mcps/joycaption-mcp`)

**Purpose**: Generate uncensored, detailed image captions for AI training datasets

**Core Features:**
- Multiple caption modes (training, descriptive, detailed_uncensored, etc.)
- Avatar name support (replace generic "woman/man" with custom names)
- Batch processing with progress tracking
- JSON metadata export alongside images
- Skip existing captions to avoid reprocessing
- Default mode: `detailed_uncensored`

**Key Files:**
- `joycaption_mcp/server.py` - Main MCP server implementation
- `batch_caption_final.py` - Clean batch processing script (captions only)
- `batch_caption.py` - Original batch processor

**Tools Exposed:**
- `caption_image`: Generate captions for single images with optional JSON export
- `caption_batch`: Process entire directories of images

**Technical Details:**
- Uses JoyCaption model (uncensored VLM based on LLaVA)
- Requires transformers 4.45+ for proper functionality
- Falls back to BLIP if JoyCaption unavailable (but BLIP is censored)

#### 2. Domain Checker MCP (`/opt/mcps/domain-checker`)

**Purpose**: Check domain availability for branding/business purposes

**Core Features:**
- Two-stage verification (DNS lookup → WHOIS query)
- 24-hour result caching to reduce redundant lookups
- Round-robin WHOIS server distribution
- Batch checking capabilities
- Detailed single domain analysis
- Clean categorized output (available/unavailable/errors)

**Key Files:**
- `domain_checker_mcp/server.py` - Main server with caching implementation
- `test_domain_checker.py` - Test script demonstrating usage

**Tools Exposed:**
- `check_domains`: Batch check multiple domains
- `check_single_domain`: Detailed check of one domain

**Technical Details:**
- DNS checks: A, AAAA, MX records
- WHOIS servers: iana.org, internic.net, verisign-grs.com, publicdomainregistry.com
- Cache stored in `~/.domain_checker_cache/domain_cache.json`
- Cache duration: 24 hours

## Current State

### What's Working
1. **JoyCaption MCP**:
   - Successfully generates uncensored captions
   - Batch processing functional with avatar names
   - JSON export working alongside images
   - Skip existing functionality prevents reprocessing

2. **Domain Checker MCP**:
   - DNS and WHOIS lookups functional
   - Caching system reduces API calls
   - Found 22 available luxury modeling domains
   - Round-robin WHOIS distribution working

### Recent Changes
- Removed attractiveness rating feature from JoyCaption (per user request)
- Added caching to domain checker for performance
- Set default caption mode to `detailed_uncensored`
- Major project reorganization with `old/` archive structure
- Created comprehensive Lourii brand story and history

### Known Issues
- BLIP model produces censored output ("frng fr frng")
- Some domains show as available with accents (technically invalid)
- WHOIS rate limiting can occur with extensive checking

## Dependencies

### JoyCaption MCP
- Python 3.10+
- transformers >= 4.45.2
- torch with CUDA support
- PIL (Pillow)
- tqdm
- mcp

### Domain Checker MCP
- Python 3.10+
- mcp >= 1.0.0
- dnspython >= 2.6.1
- python-whois >= 0.9.3

## Configuration

### Claude Code Integration
Add to Claude Code configuration file:

```json
{
  "mcpServers": {
    "joycaption": {
      "command": "python",
      "args": ["-m", "joycaption_mcp"],
      "cwd": "/opt/mcps/joycaption-mcp"
    },
    "domain-checker": {
      "command": "python", 
      "args": ["-m", "domain_checker_mcp"],
      "cwd": "/opt/mcps/domain-checker"
    }
  }
}
```

### Environment Setup
1. Create virtual environments for each server
2. Install dependencies: `pip install -e .` in each directory
3. Test with provided test scripts

## Usage Examples

### JoyCaption
```bash
# Batch process with avatar name
python batch_caption_final.py samples --avatar-name Emma

# Detailed mode
python batch_caption_final.py images --mode detailed_uncensored
```

### Domain Checker
```python
# In Claude Code
domains = ["example.com", "test.com", "myuniquedomain.com"]
result = await check_domains({"domains": domains})
```

## Related Documentation

### Domain Checker Story
- `/docs/domain-checker/Lourii.md` - Fictional brand story
- `/docs/domain-checker/Lourii_Complete_History.md` - Extended narrative

### Technical Docs
- `/docs/joycaption-mcp/` - Various technical documents
- Individual README.md files in each server directory

## Next Steps

### Immediate Priorities
1. Package and distribute MCP servers for easier installation
2. Add more caption modes to JoyCaption
3. Implement domain availability monitoring/alerts
4. Create unified testing framework

### Planned Features
1. JoyCaption: Support for video frame captioning
2. Domain Checker: Historical availability tracking
3. Both: Improved error handling and logging
4. Both: Web UI for non-technical users

## Important Context for Future Sessions

1. **User Preferences**:
   - Wants uncensored, accurate captions (why JoyCaption chosen)
   - Removed attractiveness ratings - focus on captions only
   - Prefers "detailed_uncensored" as default mode
   - Interested in luxury/fashion domain names

2. **Technical Decisions**:
   - Caching implemented to respect API rate limits
   - Transformers 4.45+ required for JoyCaption
   - Round-robin WHOIS to distribute load
   - JSON files use same name as images for easy pairing

3. **Project Philosophy**:
   - Clean, maintainable code structure
   - Comprehensive documentation
   - Practical tools that solve real problems
   - Integration with Claude Code ecosystem