#!/usr/bin/env python3
"""
Test client for the deployed Wikidata MCP Server on Render.
Tests the streamable-http transport connection and MCP functionality.
"""

import asyncio
import json
from typing import Any, Dict

async def test_remote_mcp_server():
    """Test the remote MCP server deployed on Render."""
    
    print("🔍 Testing Wikidata MCP Server on Render...")
    print("URL: https://wikidata-mcp-mirror.onrender.com")
    print()
    
    try:
        # Try to import FastMCP client components
        from mcp import ClientSession
        from mcp.client.stdio import StdioServerParameters
        from mcp.client.sse import SseServerParameters
        
        print("✅ MCP client libraries imported successfully")
        
        # Test with SSE transport first (fallback)
        print("\n1. Testing with SSE transport...")
        try:
            server_params = SseServerParameters(
                url="https://wikidata-mcp-mirror.onrender.com/sse"
            )
            
            async with ClientSession(server_params) as session:
                # Initialize the session
                await session.initialize()
                print("✅ SSE connection initialized successfully")
                
                # List available tools
                tools = await session.list_tools()
                print(f"✅ Found {len(tools.tools)} tools:")
                for tool in tools.tools[:3]:  # Show first 3 tools
                    print(f"   - {tool.name}: {tool.description}")
                
                # Test a simple tool call
                if tools.tools:
                    tool_name = tools.tools[0].name
                    print(f"\n2. Testing tool call: {tool_name}")
                    
                    result = await session.call_tool(
                        tool_name,
                        arguments={"query": "Albert Einstein"}
                    )
                    print(f"✅ Tool call successful")
                    print(f"   Result type: {type(result.content)}")
                    if result.content:
                        content_preview = str(result.content[0])[:200] + "..." if len(str(result.content[0])) > 200 else str(result.content[0])
                        print(f"   Content preview: {content_preview}")
                
                return True
                
        except Exception as sse_error:
            print(f"❌ SSE transport failed: {sse_error}")
        
        # If SSE fails, the server might not be properly configured
        print("\n❌ Unable to connect to the remote MCP server")
        print("This could indicate:")
        print("   - Server is not properly exposing MCP endpoints")
        print("   - Transport configuration mismatch")
        print("   - Server deployment issues")
        
        return False
        
    except ImportError as e:
        print(f"❌ Failed to import MCP client libraries: {e}")
        print("Make sure you have the MCP SDK installed:")
        print("   pip install mcp")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_basic_http_endpoints():
    """Test basic HTTP endpoints to understand server behavior."""
    
    print("\n🌐 Testing basic HTTP endpoints...")
    
    import aiohttp
    
    base_url = "https://wikidata-mcp-mirror.onrender.com"
    endpoints_to_test = [
        "/",
        "/health", 
        "/messages",
        "/sse",
        "/mcp",
        "/.well-known/mcp"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            try:
                async with session.get(url) as response:
                    status = response.status
                    content_type = response.headers.get('content-type', 'unknown')
                    content_length = response.headers.get('content-length', 'unknown')
                    
                    print(f"   {endpoint:20} -> {status} ({content_type}, {content_length} bytes)")
                    
                    if status == 200:
                        text = await response.text()
                        if len(text) < 200:
                            print(f"      Content: {text}")
                        else:
                            print(f"      Content preview: {text[:100]}...")
                            
            except Exception as e:
                print(f"   {endpoint:20} -> ERROR: {e}")

if __name__ == "__main__":
    print("🚀 Remote MCP Server Test Suite")
    print("=" * 50)
    
    # Run basic HTTP tests first
    asyncio.run(test_basic_http_endpoints())
    
    print("\n" + "=" * 50)
    
    # Run MCP-specific tests
    success = asyncio.run(test_remote_mcp_server())
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Remote MCP server tests completed successfully!")
    else:
        print("⚠️  Remote MCP server tests encountered issues.")
        print("Check server logs and configuration.")
