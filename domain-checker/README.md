# Domain Checker MCP Server

An MCP (Model Context Protocol) server that checks domain availability by performing DNS lookups and WHOIS queries.

## Features

- **Batch domain checking** - Check multiple domains at once
- **Two-stage verification**:
  1. DNS lookup - Quick check if domain has active DNS records
  2. WHOIS lookup - Check domain registration if no DNS found
- **Round-robin WHOIS servers** - Distributes queries across multiple public WHOIS servers
- **Detailed single domain checks** - Get comprehensive information about a specific domain
- **Clean categorized results** - Domains sorted into available, unavailable, and error categories

## Installation

1. Clone or download this directory to your MCP servers location:
```bash
cd /path/to/mcp-servers
git clone [repository] domain-checker
cd domain-checker
```

2. Install dependencies:
```bash
pip install -e .
```

Or install individual dependencies:
```bash
pip install mcp dnspython python-whois
```

## Configuration

Add to your Claude Code configuration (`~/Library/Application Support/Claude/claude.json` on macOS):

```json
{
  "mcpServers": {
    "domain-checker": {
      "command": "python",
      "args": ["-m", "domain_checker_mcp"],
      "cwd": "/path/to/domain-checker"
    }
  }
}
```

## Usage

The MCP server provides two tools:

### 1. check_domains
Check multiple domains at once:

```
domains: ["example.com", "google.com", "myuniquedomain123.com"]
```

Returns categorized results showing:
- Available domains
- Unavailable domains (with detection method)
- Errors (if any)
- Summary statistics

### 2. check_single_domain
Get detailed information about a single domain:

```
domain: "example.com"
```

Returns:
- Availability status
- Detection method (DNS or WHOIS)
- Additional details like IP addresses (if found)

## How It Works

1. **DNS Check**: First attempts to resolve DNS records (A, AAAA, MX)
   - If DNS records exist → domain is unavailable
   - If no DNS records → proceed to WHOIS check

2. **WHOIS Check**: Queries domain registration databases
   - If WHOIS record exists → domain is unavailable
   - If no WHOIS record → domain is available

3. **Round-Robin WHOIS**: Cycles through multiple public WHOIS servers:
   - whois.iana.org
   - whois.internic.net
   - whois.verisign-grs.com
   - whois.publicdomainregistry.com

## Testing

Run the included test script:

```bash
python test_domain_checker.py
```

This will:
- Test a mix of known available and unavailable domains
- Demonstrate batch checking functionality
- Show single domain detailed checks
- Test WHOIS server rotation
- Save results to `test_results.json`

## Example Output

```
=== Domain Availability Check Results ===

✅ AVAILABLE (3 domains):
  • myuniquedomain123.com
  • testing987654321.org
  • veryrandomname2025.net

❌ UNAVAILABLE (5 domains):
  • google.com (detected via dns)
  • facebook.com (detected via dns)
  • example.org (detected via whois)
  • github.com (detected via dns)
  • stackoverflow.com (detected via dns)

📊 Summary:
  Total checked: 8
  Available: 3
  Unavailable: 5
  Errors: 0
```

## Limitations

- WHOIS data accuracy depends on the registrar and TLD
- Some TLDs may have rate limiting on WHOIS queries
- DNS propagation delays might affect recently registered domains
- Some domains may show as available but have restrictions (premium, reserved, etc.)

## Dependencies

- `mcp` - Model Context Protocol SDK
- `dnspython` - DNS resolution library
- `python-whois` - WHOIS query library

## License

MIT License