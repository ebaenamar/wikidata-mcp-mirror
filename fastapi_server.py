"""
Wikidata MCP Server (SSE Version with FastAPI)

This module implements a Model Context Protocol (MCP) server with SSE transport
that connects Large Language Models to Wikidata's structured knowledge base.
Based on the implementation pattern from panz2018/fastapi_mcp_sse.
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.responses import Response
import uvicorn
from mcp.server.sse import SseServerTransport
from mcp.server.fastmcp import FastMCP

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
def get_wikidata_properties(entity_id: str) -> str:
    """
    Get properties for a Wikidata entity.
    
    Args:
        entity_id: The Wikidata entity ID (e.g., Q937)
        
    Returns:
        JSON string with entity properties
    """
    return get_entity_properties(entity_id)

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

# ============= CREATE FASTAPI APP =============

# Create FastAPI application
app = FastAPI(
    title="Wikidata MCP Server",
    description="A Model Context Protocol server that connects LLMs to Wikidata's structured knowledge base",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create SSE transport
sse = SseServerTransport("/messages")

# Mount the /messages path to handle SSE message posting
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))

@app.get("/")
async def root():
    """Root endpoint that provides basic information about the server."""
    return Response(
        content="Wikidata MCP Server is running. Use /sse for MCP connections.",
        media_type="text/plain"
    )

@app.get("/sse")
async def handle_sse(request: Request):
    """
    SSE endpoint that connects to the MCP server.
    
    This endpoint establishes a Server-Sent Events connection with the client
    and forwards communication to the Model Context Protocol server.
    """
    # Use sse.connect_sse to establish an SSE connection with the MCP server
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        # Run the MCP server with the established streams
        await mcp.connect(streams[0], streams[1])
    return Response()

# ============= SERVER EXECUTION =============

if __name__ == "__main__":
    print("Starting Wikidata MCP Server with SSE transport...")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
