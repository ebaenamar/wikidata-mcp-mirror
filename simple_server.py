"""
Simple Wikidata MCP Server with SSE Transport

A minimal implementation of an MCP server for Wikidata using SSE transport.
"""
import os
import json
import asyncio
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import uvicorn

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

from wikidata_api import (
    search_entity,
    search_property,
    get_entity_metadata,
    get_entity_properties,
    execute_sparql
)

# Initialize FastMCP
mcp = FastMCP(name="Wikidata Knowledge")

# ============= MCP TOOLS =============

@mcp.tool()
def search_wikidata_entity(query: str) -> str:
    """
    Search for a Wikidata entity by name.
    
    Args:
        query: The name of the entity to search for (e.g., "Albert Einstein")
        
    Returns:
        The Wikidata entity ID (e.g., Q937) or an error message
    """
    return search_entity(query)

@mcp.tool()
def search_wikidata_property(query: str) -> str:
    """
    Search for a Wikidata property by name.
    
    Args:
        query: The name of the property to search for (e.g., "instance of")
        
    Returns:
        The Wikidata property ID (e.g., P31) or an error message
    """
    return search_property(query)

@mcp.tool()
def get_wikidata_metadata(entity_id: str) -> str:
    """
    Get metadata for a Wikidata entity.
    
    Args:
        entity_id: The Wikidata entity ID (e.g., Q937)
        
    Returns:
        JSON string with entity metadata (label, description, aliases)
    """
    return get_entity_metadata(entity_id)

@mcp.tool()
def execute_wikidata_sparql(query: str) -> str:
    """
    Execute a SPARQL query against the Wikidata endpoint.
    
    Args:
        query: A valid SPARQL query
        
    Returns:
        JSON string with query results
    """
    return execute_sparql(query)

# ============= CREATE APP =============

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create SSE transport
sse_transport = SseServerTransport("/messages")

@app.get("/")
async def root():
    return Response(content="Wikidata MCP Server is running. Use /sse for MCP connections.")

@app.get("/sse")
async def sse_endpoint(request: Request):
    """Handle SSE connection"""
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp.connect(streams[0], streams[1])
    return Response()

# Mount messages endpoint
app.mount("/messages", sse_transport.handle_post_message)

# ============= SERVER EXECUTION =============

if __name__ == "__main__":
    print("Starting Simple Wikidata MCP Server with SSE transport...")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
