#!/usr/bin/env python3
"""
Test script for Domain Checker MCP
"""

import asyncio
import json
from domain_checker_mcp.server import DomainChecker

async def test_domain_checker():
    """Test the domain checker functionality"""
    print("=== Domain Checker Test ===\n")
    
    checker = DomainChecker()
    
    # Test domains - mix of available and unavailable
    test_domains = [
        "google.com",           # Definitely taken
        "facebook.com",         # Definitely taken
        "amazon.com",          # Definitely taken
        "xyzabc123456789.com", # Likely available
        "testing987654321.org", # Likely available
        "mysuperrandomdomain2025.net", # Likely available
        "github.com",          # Definitely taken
        "stackoverflow.com",   # Definitely taken
        "thisisaveryunlikelydomainname123456.com", # Likely available
        "wikipedia.org",       # Definitely taken
    ]
    
    print(f"Testing {len(test_domains)} domains...\n")
    
    # Test batch checking
    results = await checker.check_domains_batch(test_domains)
    
    # Display results
    print("✅ AVAILABLE DOMAINS:")
    if results['available']:
        for domain in results['available']:
            print(f"  • {domain['domain']}")
    else:
        print("  (none)")
    
    print("\n❌ UNAVAILABLE DOMAINS:")
    if results['unavailable']:
        for domain in results['unavailable']:
            print(f"  • {domain['domain']} (via {domain['method']})")
    else:
        print("  (none)")
    
    print("\n⚠️  ERRORS:")
    if results['errors']:
        for domain in results['errors']:
            print(f"  • {domain['domain']}: {domain.get('error', 'Unknown')}")
    else:
        print("  (none)")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total checked: {results['summary']['total_checked']}")
    print(f"  Available: {results['summary']['available_count']}")
    print(f"  Unavailable: {results['summary']['unavailable_count']}")
    print(f"  Errors: {results['summary']['error_count']}")
    
    # Test single domain with details
    print("\n\n=== Single Domain Test ===")
    single_domain = "example.com"
    print(f"\nChecking {single_domain} in detail...")
    
    domain_name, status, method = checker.check_domain(single_domain)
    print(f"Domain: {domain_name}")
    print(f"Status: {status}")
    print(f"Method: {method}")
    
    # Test WHOIS server rotation
    print("\n\n=== WHOIS Server Rotation Test ===")
    print("Testing round-robin WHOIS server selection:")
    for i in range(8):
        server = checker.get_next_whois_server()
        print(f"  Request {i+1}: {server}")
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\n\n✅ Full results saved to test_results.json")

if __name__ == "__main__":
    asyncio.run(test_domain_checker())