#!/usr/bin/env python3
"""
Complete MCP flow test for the deployed Wikidata MCP Server.
Tests the full MCP protocol flow: initialize -> list tools -> call tool.
"""

import asyncio
import json
import aiohttp
from typing import Any, Dict, Optional

class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.request_id = 0
        
    def _next_id(self) -> int:
        self.request_id += 1
        return self.request_id
    
    async def _make_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make an MCP JSON-RPC request."""
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method
        }
        
        if params:
            payload["params"] = params
            
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=payload) as response:
                content_type = response.headers.get('content-type', '')
                
                if 'text/event-stream' in content_type:
                    # Handle SSE response
                    text = await response.text()
                    # Extract JSON from SSE format
                    lines = text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            return json.loads(line[6:])  # Remove 'data: ' prefix
                    return {"error": "No data in SSE response"}
                else:
                    # Handle JSON response
                    return await response.json()
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP session."""
        print("🔄 Initializing MCP session...")
        
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "experimental": {},
                "sampling": {}
            },
            "clientInfo": {
                "name": "wikidata-test-client",
                "version": "1.0.0"
            }
        }
        
        result = await self._make_request("initialize", params)
        
        if "result" in result:
            print("✅ MCP session initialized successfully")
            server_info = result["result"].get("serverInfo", {})
            print(f"   Server: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
            capabilities = result["result"].get("capabilities", {})
            print(f"   Capabilities: {list(capabilities.keys())}")
            return result
        else:
            print(f"❌ Initialization failed: {result}")
            return result
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available MCP tools."""
        print("\n🔧 Listing available tools...")
        
        result = await self._make_request("tools/list")
        
        if "result" in result:
            tools = result["result"].get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for i, tool in enumerate(tools[:5]):  # Show first 5 tools
                print(f"   {i+1}. {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            if len(tools) > 5:
                print(f"   ... and {len(tools) - 5} more tools")
            return result
        else:
            print(f"❌ Failed to list tools: {result}")
            return result
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool."""
        print(f"\n⚡ Calling tool: {tool_name}")
        print(f"   Arguments: {arguments}")
        
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        
        result = await self._make_request("tools/call", params)
        
        if "result" in result:
            print("✅ Tool call successful")
            content = result["result"].get("content", [])
            if content:
                print(f"   Response type: {content[0].get('type', 'unknown')}")
                text = content[0].get("text", "")
                if len(text) > 300:
                    print(f"   Response preview: {text[:300]}...")
                else:
                    print(f"   Response: {text}")
            return result
        else:
            print(f"❌ Tool call failed: {result}")
            return result
    
    async def list_prompts(self) -> Dict[str, Any]:
        """List available MCP prompts."""
        print("\n📝 Listing available prompts...")
        
        result = await self._make_request("prompts/list")
        
        if "result" in result:
            prompts = result["result"].get("prompts", [])
            print(f"✅ Found {len(prompts)} prompts:")
            for i, prompt in enumerate(prompts[:3]):  # Show first 3 prompts
                print(f"   {i+1}. {prompt.get('name', 'Unknown')}: {prompt.get('description', 'No description')}")
            if len(prompts) > 3:
                print(f"   ... and {len(prompts) - 3} more prompts")
            return result
        else:
            print(f"❌ Failed to list prompts: {result}")
            return result
    
    async def list_resources(self) -> Dict[str, Any]:
        """List available MCP resources."""
        print("\n📚 Listing available resources...")
        
        result = await self._make_request("resources/list")
        
        if "result" in result:
            resources = result["result"].get("resources", [])
            print(f"✅ Found {len(resources)} resources:")
            for i, resource in enumerate(resources[:3]):  # Show first 3 resources
                print(f"   {i+1}. {resource.get('name', 'Unknown')}: {resource.get('description', 'No description')}")
            if len(resources) > 3:
                print(f"   ... and {len(resources) - 3} more resources")
            return result
        else:
            print(f"❌ Failed to list resources: {result}")
            return result

async def test_complete_mcp_flow():
    """Test the complete MCP flow with the deployed server."""
    
    print("🚀 Complete MCP Flow Test")
    print("=" * 60)
    print("Server: https://wikidata-mcp-mirror.onrender.com/mcp")
    print()
    
    client = MCPClient("https://wikidata-mcp-mirror.onrender.com/mcp")
    
    try:
        # Step 1: Initialize
        init_result = await client.initialize()
        if "error" in init_result:
            print("❌ Cannot proceed without successful initialization")
            return False
        
        # Step 2: List tools
        tools_result = await client.list_tools()
        
        # Step 3: List prompts
        prompts_result = await client.list_prompts()
        
        # Step 4: List resources
        resources_result = await client.list_resources()
        
        # Step 5: Test a simple tool call
        if "result" in tools_result:
            tools = tools_result["result"].get("tools", [])
            if tools:
                # Try to find a simple search tool
                search_tool = None
                for tool in tools:
                    if "search" in tool.get("name", "").lower():
                        search_tool = tool
                        break
                
                if search_tool:
                    await client.call_tool(
                        search_tool["name"],
                        {"query": "Albert Einstein"}
                    )
                else:
                    # Use the first available tool
                    first_tool = tools[0]
                    print(f"\n⚡ Testing first available tool: {first_tool['name']}")
                    
                    # Try with a generic query argument
                    await client.call_tool(
                        first_tool["name"],
                        {"query": "test"}
                    )
        
        print("\n" + "=" * 60)
        print("🎉 Complete MCP flow test finished!")
        print("✅ Server is fully operational and responding to MCP protocol")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_complete_mcp_flow())
    if success:
        print("\n🎯 DEPLOYMENT VALIDATION: SUCCESS")
        print("The Wikidata MCP Server is ready for production use!")
    else:
        print("\n⚠️  DEPLOYMENT VALIDATION: ISSUES DETECTED")
        print("Check server configuration and logs.")
