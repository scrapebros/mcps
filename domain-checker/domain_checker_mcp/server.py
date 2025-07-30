"""
Domain Checker MCP Server

Checks domain availability by:
1. DNS lookup - if domain resolves, it's taken
2. WHOIS lookup - if no DNS but WHOIS exists, it's taken
3. Otherwise - domain is available
"""

import asyncio
import json
import logging
import socket
import random
from typing import Any, Dict, List, Tuple
from datetime import datetime, timedelta
import os
from pathlib import Path

import dns.resolver
import whois
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Public WHOIS servers to round-robin through
WHOIS_SERVERS = [
    "whois.iana.org",
    "whois.internic.net",
    "whois.verisign-grs.com",
    "whois.publicdomainregistry.com",
]

class DomainChecker:
    def __init__(self):
        self.whois_index = 0
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 5  # 5 second timeout
        self.resolver.lifetime = 5
        
        # Cache setup
        self.cache_dir = Path.home() / ".domain_checker_cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "domain_cache.json"
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
        self.cache = self.load_cache()
        
    def get_next_whois_server(self) -> str:
        """Get next WHOIS server in round-robin fashion"""
        server = WHOIS_SERVERS[self.whois_index]
        self.whois_index = (self.whois_index + 1) % len(WHOIS_SERVERS)
        return server
    
    def load_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def get_cached_result(self, domain: str) -> Tuple[str, str, str] | None:
        """Get cached result if valid"""
        if domain in self.cache:
            cache_entry = self.cache[domain]
            cached_time = datetime.fromisoformat(cache_entry['timestamp'])
            if datetime.now() - cached_time < self.cache_duration:
                return (domain, cache_entry['status'], cache_entry['method'])
        return None
    
    def cache_result(self, domain: str, status: str, method: str):
        """Cache domain check result"""
        self.cache[domain] = {
            'status': status,
            'method': method,
            'timestamp': datetime.now().isoformat()
        }
        self.save_cache()
    
    def check_dns(self, domain: str) -> bool:
        """Check if domain has DNS records"""
        try:
            # Try to resolve A records
            self.resolver.resolve(domain, 'A')
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, Exception):
            pass
            
        try:
            # Try to resolve AAAA records (IPv6)
            self.resolver.resolve(domain, 'AAAA')
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, Exception):
            pass
            
        try:
            # Try to resolve MX records
            self.resolver.resolve(domain, 'MX')
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, Exception):
            pass
            
        return False
    
    def check_whois(self, domain: str) -> bool:
        """Check if domain exists in WHOIS"""
        try:
            # Try with python-whois first
            w = whois.whois(domain)
            
            # Check if we got meaningful data
            if w.domain_name:
                return True
            if w.status:
                return True
            if w.creation_date:
                return True
            if w.registrar:
                return True
                
            return False
            
        except Exception as e:
            logger.debug(f"WHOIS lookup failed for {domain}: {e}")
            return False
    
    def check_domain(self, domain: str) -> Tuple[str, str, str]:
        """
        Check domain availability
        Returns: (domain, status, method)
        status: 'available' or 'unavailable'
        method: 'dns' or 'whois' or 'error' or 'cached'
        """
        # Clean domain
        domain = domain.lower().strip()
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check cache first
        cached_result = self.get_cached_result(domain)
        if cached_result:
            domain_name, status, method = cached_result
            return (domain_name, status, f"{method}_cached")
        
        try:
            # First check DNS
            if self.check_dns(domain):
                self.cache_result(domain, 'unavailable', 'dns')
                return (domain, 'unavailable', 'dns')
            
            # If no DNS, check WHOIS
            if self.check_whois(domain):
                self.cache_result(domain, 'unavailable', 'whois')
                return (domain, 'unavailable', 'whois')
            
            # If neither DNS nor WHOIS, domain is available
            self.cache_result(domain, 'available', 'none')
            return (domain, 'available', 'none')
            
        except Exception as e:
            logger.error(f"Error checking domain {domain}: {e}")
            return (domain, 'error', str(e))
    
    async def check_domains_batch(self, domains: List[str]) -> Dict[str, List[Dict[str, str]]]:
        """Check multiple domains and return categorized results"""
        available = []
        unavailable = []
        errors = []
        
        for domain in domains:
            domain_name, status, method = self.check_domain(domain)
            
            result = {
                'domain': domain_name,
                'method': method.replace('_cached', '') if '_cached' in method else method,
                'timestamp': datetime.now().isoformat(),
                'cached': '_cached' in method
            }
            
            if status == 'available':
                available.append(result)
            elif status == 'unavailable':
                unavailable.append(result)
            else:
                result['error'] = method
                errors.append(result)
        
        return {
            'available': available,
            'unavailable': unavailable,
            'errors': errors,
            'summary': {
                'total_checked': len(domains),
                'available_count': len(available),
                'unavailable_count': len(unavailable),
                'error_count': len(errors)
            }
        }

# Create server instance
app = Server("domain-checker")
checker = DomainChecker()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="check_domains",
            description="Check availability of multiple domains",
            inputSchema={
                "type": "object",
                "properties": {
                    "domains": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of domain names to check (without http/https)"
                    }
                },
                "required": ["domains"]
            }
        ),
        Tool(
            name="check_single_domain",
            description="Check availability of a single domain with detailed info",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain name to check (without http/https)"
                    }
                },
                "required": ["domain"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    if name == "check_domains":
        try:
            domains = arguments.get("domains", [])
            if not domains:
                return [TextContent(text="Error: No domains provided")]
            
            # Check domains
            results = await checker.check_domains_batch(domains)
            
            # Format results
            output = []
            output.append("=== Domain Availability Check Results ===\n")
            
            # Available domains
            if results['available']:
                output.append(f"\n✅ AVAILABLE ({len(results['available'])} domains):")
                for domain in results['available']:
                    output.append(f"  • {domain['domain']}")
            
            # Unavailable domains
            if results['unavailable']:
                output.append(f"\n❌ UNAVAILABLE ({len(results['unavailable'])} domains):")
                for domain in results['unavailable']:
                    cached_str = " [cached]" if domain.get('cached', False) else ""
                    output.append(f"  • {domain['domain']} (detected via {domain['method']}){cached_str}")
            
            # Errors
            if results['errors']:
                output.append(f"\n⚠️  ERRORS ({len(results['errors'])} domains):")
                for domain in results['errors']:
                    output.append(f"  • {domain['domain']}: {domain.get('error', 'Unknown error')}")
            
            # Summary
            output.append(f"\n📊 Summary:")
            output.append(f"  Total checked: {results['summary']['total_checked']}")
            output.append(f"  Available: {results['summary']['available_count']}")
            output.append(f"  Unavailable: {results['summary']['unavailable_count']}")
            output.append(f"  Errors: {results['summary']['error_count']}")
            
            # Add JSON results
            output.append(f"\n📋 Full Results (JSON):")
            output.append(json.dumps(results, indent=2))
            
            return [TextContent(text="\n".join(output))]
            
        except Exception as e:
            logger.error(f"Error in check_domains: {e}")
            return [TextContent(text=f"Error checking domains: {str(e)}")]
    
    elif name == "check_single_domain":
        try:
            domain = arguments.get("domain", "").strip()
            if not domain:
                return [TextContent(text="Error: No domain provided")]
            
            # Check single domain with detailed info
            domain_name, status, method = checker.check_domain(domain)
            
            output = []
            output.append(f"=== Domain Check: {domain_name} ===\n")
            
            if status == 'available':
                output.append("✅ Status: AVAILABLE")
                output.append("This domain appears to be available for registration!")
                output.append(f"• No DNS records found")
                output.append(f"• No WHOIS registration found")
            elif status == 'unavailable':
                output.append("❌ Status: UNAVAILABLE")
                output.append("This domain is already registered.")
                output.append(f"• Detection method: {method}")
                
                # Add more details based on method
                if method == 'dns':
                    output.append("• Domain has active DNS records")
                    try:
                        # Try to get IP addresses
                        ips = []
                        try:
                            for answer in checker.resolver.resolve(domain_name, 'A'):
                                ips.append(str(answer))
                        except:
                            pass
                        if ips:
                            output.append(f"• IP addresses: {', '.join(ips)}")
                    except:
                        pass
                elif method == 'whois':
                    output.append("• Domain found in WHOIS database")
                    output.append("• No active DNS records")
            else:
                output.append(f"⚠️  Status: ERROR")
                output.append(f"• Error: {method}")
            
            output.append(f"\n• Check timestamp: {datetime.now().isoformat()}")
            
            return [TextContent(text="\n".join(output))]
            
        except Exception as e:
            logger.error(f"Error in check_single_domain: {e}")
            return [TextContent(text=f"Error checking domain: {str(e)}")]
    
    else:
        return [TextContent(text=f"Error: Unknown tool: {name}")]

def main():
    """Main entry point"""
    logger.info("Starting Domain Checker MCP server...")
    asyncio.run(stdio_server(app).run())

if __name__ == "__main__":
    main()