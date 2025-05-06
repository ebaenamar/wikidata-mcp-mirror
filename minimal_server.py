"""
Minimal Wikidata MCP Server with SSE Transport

A simplified implementation focused on basic functionality.
"""
import os
import json
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
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

# ============= FASTAPI APP =============

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Wikidata MCP Server is running. Use /sse for MCP connections."}

# ============= DIRECT MCP IMPLEMENTATION =============

# Store active SSE connections
active_connections = {}

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP connections"""
    print(f"SSE connection request received from: {request.client}")
    
    async def event_generator():
        # Generate a unique session ID
        import uuid
        session_id = str(uuid.uuid4())
        print(f"Created new session: {session_id}")
        
        # Store connection info
        from asyncio import Queue
        read_queue = Queue()
        write_queue = Queue()
        active_connections[session_id] = {
            "read_queue": read_queue,
            "write_queue": write_queue,
            "created_at": import_time()
        }
        
        # Send initial message with session ID
        yield f"event: endpoint\ndata: /messages?session_id={session_id}\n\n"
        
        # Run MCP server in the background
        import asyncio
        asyncio.create_task(
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
        finally:
            # Clean up
            ping_task.cancel()
            if session_id in active_connections:
                del active_connections[session_id]
            print(f"Closed session: {session_id}")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/messages")
async def messages_endpoint(request: Request):
    """Handle messages from the client"""
    # Get session ID from query parameters
    session_id = request.query_params.get("session_id")
    if not session_id or session_id not in active_connections:
        return Response(content="Invalid session ID", status_code=400)
    
    # Get message from request body
    body = await request.body()
    message = body.decode("utf-8")
    
    # Put message in the read queue
    await active_connections[session_id]["read_queue"].put(message)
    
    return Response(status_code=200)

async def run_mcp_server(read_queue, write_queue, session_id):
    """Run the MCP server with the given queues"""
    print(f"Starting MCP server for session: {session_id}")
    try:
        # Create stream adapters
        from mcp.transport.stream import QueueReadStream, QueueWriteStream
        read_stream = QueueReadStream(read_queue)
        write_stream = QueueWriteStream(write_queue)
        
        # Run MCP server
        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            mcp._mcp_server.create_initialization_options()
        )
    except Exception as e:
        print(f"Error in MCP server for session {session_id}: {str(e)}")
        import traceback
        print(traceback.format_exc())
    finally:
        # Signal to close the connection
        await write_queue.put(None)
        print(f"MCP server stopped for session: {session_id}")

async def send_periodic_pings(session_id):
    """Send periodic pings to keep the connection alive"""
    import asyncio
    from datetime import datetime
    
    while session_id in active_connections:
        # Send a ping comment every 15 seconds
        await asyncio.sleep(15)
        if session_id in active_connections:
            write_queue = active_connections[session_id]["write_queue"]
            await write_queue.put(f": ping - {datetime.now().isoformat()}")

def import_time():
    """Import time module and return current time"""
    from datetime import datetime
    return datetime.now()

# ============= SERVER EXECUTION =============

if __name__ == "__main__":
    print("Starting Minimal Wikidata MCP Server...")
    port = int(os.environ.get("PORT", 8000))
    
    # Configure uvicorn with optimized settings
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        timeout_keep_alive=300,  # 5 minutes
        log_level="info"
    )
