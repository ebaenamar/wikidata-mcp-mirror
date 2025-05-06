"""
Optimized Wikidata MCP Server with SSE Transport for Render.com

This implementation is specifically designed to work well with Render's free tier.
"""
import os
import json
import asyncio
import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from uuid import uuid4

from wikidata_api import (
    search_entity,
    search_property,
    get_entity_metadata,
    get_entity_properties,
    execute_sparql
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("wikidata-mcp")

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
    logger.info(f"Searching for entity: {query}")
    result = search_entity(query)
    logger.info(f"Entity search result: {result[:100]}...")
    return result

@mcp.tool()
def search_wikidata_property(query: str) -> str:
    """
    Search for a Wikidata property by name.
    
    Args:
        query: The name of the property to search for (e.g., "instance of")
        
    Returns:
        The Wikidata property ID (e.g., P31) or an error message
    """
    logger.info(f"Searching for property: {query}")
    result = search_property(query)
    logger.info(f"Property search result: {result[:100]}...")
    return result

@mcp.tool()
def get_wikidata_metadata(entity_id: str) -> str:
    """
    Get metadata for a Wikidata entity.
    
    Args:
        entity_id: The Wikidata entity ID (e.g., Q937)
        
    Returns:
        JSON string with entity metadata (label, description, aliases)
    """
    logger.info(f"Getting metadata for entity: {entity_id}")
    result = get_entity_metadata(entity_id)
    logger.info(f"Metadata result: {result[:100]}...")
    return result

@mcp.tool()
def get_wikidata_properties(entity_id: str) -> str:
    """
    Get properties for a Wikidata entity.
    
    Args:
        entity_id: The Wikidata entity ID (e.g., Q937)
        
    Returns:
        JSON string with entity properties
    """
    logger.info(f"Getting properties for entity: {entity_id}")
    result = get_entity_properties(entity_id)
    logger.info(f"Properties result: {result[:100]}...")
    return result

@mcp.tool()
def execute_wikidata_sparql(query: str) -> str:
    """
    Execute a SPARQL query against the Wikidata endpoint.
    
    Args:
        query: A valid SPARQL query
        
    Returns:
        JSON string with query results
    """
    logger.info(f"Executing SPARQL query: {query[:100]}...")
    result = execute_sparql(query)
    logger.info(f"SPARQL result: {result[:100]}...")
    return result

# ============= FASTAPI APP =============

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Store active SSE connections
active_connections = {}

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {"message": "Wikidata MCP Server is running. Use /sse for MCP connections."}

@app.get("/health")
async def health():
    """Health check endpoint for Render"""
    return {"status": "healthy", "connections": len(active_connections)}

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP connections"""
    client_host = request.client.host if hasattr(request, 'client') and request.client else "unknown"
    logger.info(f"SSE connection request received from: {client_host}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    # Generate a unique session ID
    session_id = str(uuid4())
    logger.info(f"Created new session: {session_id}")
    
    # Store connection info
    read_queue = asyncio.Queue()
    write_queue = asyncio.Queue()
    active_connections[session_id] = {
        "read_queue": read_queue,
        "write_queue": write_queue,
        "created_at": datetime.now(),
        "client_host": client_host
    }
    
    # Define the event generator function
    async def generate():
        # Send initial message with session ID
        yield f"event: endpoint\ndata: /messages?session_id={session_id}\n\n"
        
        # Run MCP server in the background
        mcp_task = asyncio.create_task(
            run_mcp_server(read_queue, write_queue, session_id)
        )
        
        # Keep connection alive with periodic pings
        ping_task = asyncio.create_task(
            send_periodic_pings(session_id)
        )
        
        try:
            # Forward messages from the write queue to the client
            while True:
                message = await write_queue.get()
                if message is None:  # None is our signal to close the connection
                    break
                yield f"data: {message}\n\n"
                logger.debug(f"Sent message to client: {message[:50]}...")
        finally:
            # Clean up
            ping_task.cancel()
            if not mcp_task.done():
                mcp_task.cancel()
            if session_id in active_connections:
                del active_connections[session_id]
            logger.info(f"Closed session: {session_id}")
    
    # Return a streaming response with the correct headers
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Content-Type": "text/event-stream"
        }
    )

@app.post("/messages")
async def messages_endpoint(request: Request):
    """Handle messages from the client"""
    # Get session ID from query parameters
    session_id = request.query_params.get("session_id")
    if not session_id or session_id not in active_connections:
        logger.warning(f"Invalid session ID: {session_id}")
        return Response(content="Invalid session ID", status_code=400)
    
    # Get message from request body
    body = await request.body()
    message = body.decode("utf-8")
    logger.debug(f"Received message from client: {message[:50]}...")
    
    # Put message in the read queue
    await active_connections[session_id]["read_queue"].put(message)
    
    return Response(status_code=200)

async def run_mcp_server(read_queue, write_queue, session_id):
    """Run the MCP server with the given queues"""
    logger.info(f"Starting MCP server for session: {session_id}")
    try:
        # Create stream adapters
        from mcp.transport.stream import QueueReadStream, QueueWriteStream
        read_stream = QueueReadStream(read_queue)
        write_stream = QueueWriteStream(write_queue)
        
        # Create initialization options with extended timeout
        init_options = mcp._mcp_server.create_initialization_options()
        init_options["timeoutMs"] = 300000  # 5 minutes
        
        # Run MCP server
        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            init_options
        )
        logger.info(f"MCP server completed normally for session: {session_id}")
    except asyncio.CancelledError:
        logger.info(f"MCP server cancelled for session: {session_id}")
    except Exception as e:
        logger.error(f"Error in MCP server for session {session_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Signal to close the connection
        await write_queue.put(None)
        logger.info(f"MCP server stopped for session: {session_id}")

async def send_periodic_pings(session_id):
    """Send periodic pings to keep the connection alive"""
    try:
        while session_id in active_connections:
            # Send a ping comment every 10 seconds
            await asyncio.sleep(10)
            if session_id in active_connections:
                write_queue = active_connections[session_id]["write_queue"]
                ping_message = f": ping - {datetime.now().isoformat()}"
                await write_queue.put(ping_message)
                logger.debug(f"Sent ping to session {session_id}")
    except asyncio.CancelledError:
        logger.info(f"Ping task cancelled for session: {session_id}")
    except Exception as e:
        logger.error(f"Error in ping task for session {session_id}: {str(e)}")

# ============= SERVER EXECUTION =============

if __name__ == "__main__":
    logger.info("Starting Optimized Wikidata MCP Server for Render.com...")
    port = int(os.environ.get("PORT", 10000))
    
    # Configure uvicorn with optimized settings for Render
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        timeout_keep_alive=300,  # 5 minutes
        log_level="info"
    )
