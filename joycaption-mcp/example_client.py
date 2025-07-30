#!/usr/bin/env python3
"""
Example client showing how to use the JoyCaption MCP server
"""

import asyncio
import json
from pathlib import Path

# This is a simplified example showing the MCP protocol structure
# In practice, you would use an MCP client library

async def example_mcp_calls():
    """
    Example of MCP protocol calls to the JoyCaption server
    These show the JSON-RPC format that would be sent to the server
    """
    
    print("JoyCaption MCP Server - Example Client Calls")
    print("=" * 60)
    
    # Example 1: List available tools
    print("\n1. List available tools:")
    list_tools_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    print(f"Request: {json.dumps(list_tools_request, indent=2)}")
    
    # Example 2: List caption modes
    print("\n2. List caption modes:")
    list_modes_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "list_caption_modes",
            "arguments": {}
        },
        "id": 2
    }
    print(f"Request: {json.dumps(list_modes_request, indent=2)}")
    
    # Example 3: Caption an image with default settings
    print("\n3. Caption an image (default settings):")
    caption_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "caption_image",
            "arguments": {
                "image_path": "/path/to/your/image.jpg"
            }
        },
        "id": 3
    }
    print(f"Request: {json.dumps(caption_request, indent=2)}")
    
    # Example 4: Caption with specific mode and options
    print("\n4. Caption with specific mode and options:")
    advanced_caption_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "caption_image",
            "arguments": {
                "image_path": "/path/to/your/image.jpg",
                "mode": "art_critic",
                "create_json": True,
                "extra_options": ["lighting", "composition", "aesthetic_quality"],
                "temperature": 0.7,
                "max_tokens": 1024
            }
        },
        "id": 4
    }
    print(f"Request: {json.dumps(advanced_caption_request, indent=2)}")
    
    # Example 5: Multiple caption modes for comparison
    print("\n5. Generate captions in multiple modes:")
    modes_to_test = ["descriptive", "straightforward", "stable_diffusion", "social_media"]
    
    for i, mode in enumerate(modes_to_test, start=5):
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "caption_image",
                "arguments": {
                    "image_path": "/path/to/your/image.jpg",
                    "mode": mode,
                    "word_count": 100
                }
            },
            "id": i
        }
        print(f"\n  Mode '{mode}': {json.dumps(request['params']['arguments'], indent=4)}")

def print_usage_examples():
    """Print usage examples for different scenarios"""
    
    print("\n" + "=" * 60)
    print("USAGE EXAMPLES")
    print("=" * 60)
    
    examples = [
        {
            "title": "Fine-tuning dataset caption",
            "description": "Generate descriptive captions with JSON files for a dataset",
            "arguments": {
                "image_path": "dataset/image_001.jpg",
                "mode": "descriptive",
                "create_json": True,
                "extra_options": ["no_resolution", "text_to_image"]
            }
        },
        {
            "title": "Social media post",
            "description": "Generate engaging captions for social media",
            "arguments": {
                "image_path": "photos/vacation.jpg",
                "mode": "social_media",
                "word_count": 50,
                "temperature": 0.8
            }
        },
        {
            "title": "Art analysis",
            "description": "Detailed art critique for a painting",
            "arguments": {
                "image_path": "artwork/painting.jpg",
                "mode": "art_critic",
                "extra_options": ["composition", "aesthetic_quality", "lighting"],
                "max_tokens": 1024
            }
        },
        {
            "title": "Stable Diffusion training",
            "description": "Generate prompts for SD training",
            "arguments": {
                "image_path": "training/img_001.png",
                "mode": "stable_diffusion",
                "create_json": True,
                "length": "medium"
            }
        },
        {
            "title": "Product listing",
            "description": "E-commerce product descriptions",
            "arguments": {
                "image_path": "products/item_123.jpg",
                "mode": "product_listing",
                "extra_options": ["important_only"],
                "word_count": 150
            }
        }
    ]
    
    for example in examples:
        print(f"\n### {example['title']}")
        print(f"{example['description']}")
        print(f"Arguments: {json.dumps(example['arguments'], indent=2)}")

def main():
    """Main function"""
    
    # Show example MCP calls
    asyncio.run(example_mcp_calls())
    
    # Show usage examples
    print_usage_examples()
    
    print("\n" + "=" * 60)
    print("NOTES:")
    print("- These are example JSON-RPC calls in MCP protocol format")
    print("- In practice, use an MCP client library or Claude Code")
    print("- The server handles model loading automatically")
    print("- First run will download the ~15GB model")
    print("=" * 60)

if __name__ == "__main__":
    main()