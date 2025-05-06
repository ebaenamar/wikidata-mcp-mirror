"""
Wikidata MCP Server with SSE Transport

This module implements a Model Context Protocol (MCP) server with SSE transport
that connects Large Language Models to Wikidata's structured knowledge base.
"""
import os
import json
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from mcp.server.sse import SseServerTransport
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from uuid import uuid4

from mcp.server.fastmcp.prompts import base
from starlette.routing import Route, Mount
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
    Get metadata (label and description) for a Wikidata entity.
    
    Args:
        entity_id: The Wikidata entity ID (e.g., Q937)
        
    Returns:
        JSON string containing the entity's label and description
    """
    metadata = get_entity_metadata(entity_id)
    return json.dumps(metadata)

@mcp.tool()
def get_wikidata_properties(entity_id: str) -> str:
    """
    Get all properties for a Wikidata entity.
    
    Args:
        entity_id: The Wikidata entity ID (e.g., Q937)
        
    Returns:
        JSON string containing the entity's properties and their values
    """
    properties = get_entity_properties(entity_id)
    return json.dumps(properties)

@mcp.tool()
def execute_wikidata_sparql(sparql_query: str) -> str:
    """
    Execute a SPARQL query on Wikidata.
    
    Args:
        sparql_query: SPARQL query to execute
        
    Returns:
        JSON-formatted result of the query
    """
    return execute_sparql(sparql_query)

@mcp.tool()
def find_entity_facts(entity_name: str, property_name: str = None) -> str:
    """
    Search for an entity and find its facts, optionally filtering by a property.
    
    Args:
        entity_name: The name of the entity to search for
        property_name: Optional name of a property to filter by
        
    Returns:
        A JSON string containing the entity facts
    """
    # Search for the entity
    entity_id = search_entity(entity_name)
    if entity_id == "No entity found":
        return json.dumps({"error": f"No entity found for '{entity_name}'"})
    
    # Get metadata
    metadata = get_entity_metadata(entity_id)
    
    # If a property is specified, search for it
    property_id = None
    if property_name:
        property_id = search_property(property_name)
        if property_id == "No property found":
            return json.dumps({
                "entity": metadata,
                "error": f"No property found for '{property_name}'"
            })
    
    # Build and execute SPARQL query
    if property_id:
        # Specific property query
        sparql_query = f"""
        SELECT ?value ?valueLabel
        WHERE {{
          wd:{entity_id} wdt:{property_id} ?value.
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
    else:
        # General entity info query
        sparql_query = f"""
        SELECT ?property ?propertyLabel ?value ?valueLabel
        WHERE {{
          wd:{entity_id} ?p ?statement.
          ?statement ?ps ?value.
          
          ?property wikibase:claim ?p.
          ?property wikibase:statementProperty ?ps.
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 10
        """
    
    facts = execute_sparql(sparql_query)
    
    # Combine all results
    return json.dumps({
        "entity": metadata,
        "property": {"id": property_id, "name": property_name} if property_id else None,
        "facts": json.loads(facts)
    })

@mcp.tool()
def get_related_entities(entity_id: str, relation_property: str = None, limit: int = 10) -> str:
    """
    Find entities related to the given entity, optionally by a specific relation.
    
    Args:
        entity_id: The Wikidata entity ID (e.g., Q937)
        relation_property: Optional Wikidata property ID for the relation (e.g., P31)
        limit: Maximum number of results to return
        
    Returns:
        JSON string containing related entities
    """
    if relation_property:
        # Query for specific relation
        sparql_query = f"""
        SELECT ?related ?relatedLabel
        WHERE {{
          wd:{entity_id} wdt:{relation_property} ?related.
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {limit}
        """
    else:
        # Query for any relation
        sparql_query = f"""
        SELECT ?relation ?relationLabel ?related ?relatedLabel
        WHERE {{
          wd:{entity_id} ?p ?related.
          ?property wikibase:directClaim ?p.
          BIND(?property as ?relation)
          
          # Filter out some common non-entity relations
          FILTER(STRSTARTS(STR(?related), "http://www.wikidata.org/entity/"))
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {limit}
        """
    
    return execute_sparql(sparql_query)

# ============= MCP RESOURCES =============

@mcp.resource("wikidata://common-properties")
def common_properties_resource():
    """
    Provides a list of commonly used Wikidata properties.
    """
    return {
        "properties": {
            "P31": "instance of",
            "P279": "subclass of",
            "P569": "date of birth",
            "P570": "date of death",
            "P21": "sex or gender",
            "P27": "country of citizenship",
            "P106": "occupation",
            "P17": "country",
            "P131": "located in administrative entity",
            "P50": "author",
            "P57": "director",
            "P136": "genre",
            "P577": "publication date",
            "P580": "start time",
            "P582": "end time",
            "P361": "part of",
            "P527": "has part",
            "P39": "position held",
            "P800": "notable work",
            "P1412": "languages spoken, written or signed"
        },
        "description": "Common Wikidata properties that can be used to query for specific information about entities."
    }

@mcp.resource("wikidata://sparql-examples")
def sparql_examples_resource():
    """
    Provides example SPARQL queries for common Wikidata tasks.
    """
    return {
        "examples": [
            {
                "name": "Basic entity information",
                "query": """
                SELECT ?property ?propertyLabel ?value ?valueLabel
                WHERE {
                  wd:Q937 ?p ?statement.  # Q937 = Albert Einstein
                  ?statement ?ps ?value.
                  
                  ?property wikibase:claim ?p.
                  ?property wikibase:statementProperty ?ps.
                  
                  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
                }
                LIMIT 10
                """
            },
            {
                "name": "Find all scientists",
                "query": """
                SELECT ?scientist ?scientistLabel
                WHERE {
                  ?scientist wdt:P106 wd:Q901.  # P106 = occupation, Q901 = scientist
                  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
                }
                LIMIT 20
                """
            },
            {
                "name": "Find books by an author",
                "query": """
                SELECT ?book ?bookLabel
                WHERE {
                  ?book wdt:P50 wd:Q535.  # P50 = author, Q535 = Isaac Asimov
                  ?book wdt:P31/wdt:P279* wd:Q571.  # P31 = instance of, P279 = subclass of, Q571 = book
                  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
                }
                """
            },
            {
                "name": "Find capitals of countries",
                "query": """
                SELECT ?country ?countryLabel ?capital ?capitalLabel
                WHERE {
                  ?country wdt:P31 wd:Q6256.  # P31 = instance of, Q6256 = country
                  ?country wdt:P36 ?capital.  # P36 = capital
                  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
                }
                """
            },
            {
                "name": "Find mountains higher than 8000m",
                "query": """
                SELECT ?mountain ?mountainLabel ?height
                WHERE {
                  ?mountain wdt:P31/wdt:P279* wd:Q8502.  # P31 = instance of, P279 = subclass of, Q8502 = mountain
                  ?mountain wdt:P2044 ?height.  # P2044 = elevation above sea level
                  FILTER(?height > 8000)
                  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
                }
                ORDER BY DESC(?height)
                """
            }
        ],
        "description": "Example SPARQL queries for common Wikidata tasks. These can be used as templates for more specific queries."
    }

# ============= PROMPT TEMPLATES =============

@mcp.prompt()
def entity_search_template(entity_name: str) -> list[base.Message]:
    """
    Template for searching a Wikidata entity.
    """
    return [
        base.UserMessage(f"""
You need to find information about {entity_name} in Wikidata.

Follow these steps:
1. First, search for the entity ID using search_wikidata_entity.
2. Then, get the metadata using get_wikidata_metadata.
3. Finally, execute a SPARQL query to get detailed information.
""")
    ]

@mcp.prompt()
def property_search_template(property_name: str) -> list[base.Message]:
    """
    Template for searching a Wikidata property.
    """
    return [
        base.UserMessage(f"""
You need to find information about the property "{property_name}" in Wikidata.

Follow these steps:
1. First, search for the property ID using search_wikidata_property.
2. Then, use this property ID in a SPARQL query to find entities with this property.
""")
    ]

@mcp.prompt()
def entity_relation_template(entity1_name: str, entity2_name: str) -> list[base.Message]:
    """
    Template for finding relationships between entities.
    """
    return [
        base.UserMessage(f"""
You need to find the relationship between {entity1_name} and {entity2_name} in Wikidata.

Follow these steps:
1. First, search for both entity IDs using search_wikidata_entity.
2. Then, execute a SPARQL query to find direct or indirect relationships between them.
""")
    ]

# ============= CREATE SSE APP =============

# Configure SSE transport
sse_transport = SseServerTransport("/messages")

# Create FastAPI app with explicit CORS configuration
app = FastAPI()

# Add CORS middleware with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Store active SSE connections
active_connections = {}

# Define root endpoint
@app.get("/")
async def root():
    print("Root endpoint accessed")
    return Response(content="Wikidata MCP Server is running. Use /sse for MCP connections.")

@app.get("/health")
async def health():
    """Health check endpoint for Render"""
    return {"status": "healthy", "connections": len(active_connections)}

# Define SSE endpoint
@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP connections"""
    client_host = request.client.host if hasattr(request, 'client') and request.client else "unknown"
    print(f"SSE connection request received from: {client_host}")
    print(f"Request headers: {dict(request.headers)}")
    
    # Generate a unique session ID
    session_id = str(uuid4())
    print(f"Created new session: {session_id}")
    
    # Store connection info
    from asyncio import Queue
    read_queue = Queue()
    write_queue = Queue()
    from datetime import datetime
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
        import asyncio
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
                print(f"Sent message to client: {message[:50]}...")
        finally:
            # Clean up
            ping_task.cancel()
            if not mcp_task.done():
                mcp_task.cancel()
            if session_id in active_connections:
                del active_connections[session_id]
            print(f"Closed session: {session_id}")
    
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

# Define explicit POST endpoint for messages
@app.post("/messages")
async def post_messages(request: Request):
    """Explicitly handle POST requests to /messages"""
    # Get session ID from query parameters
    session_id = request.query_params.get("session_id")
    if not session_id or session_id not in active_connections:
        print(f"Invalid session ID: {session_id}")
        return Response(content="Invalid session ID", status_code=400)
    
    # Get message from request body
    body = await request.body()
    message = body.decode("utf-8")
    print(f"Received message from client: {message[:50]}...")
    
    # Put message in the read queue
    await active_connections[session_id]["read_queue"].put(message)
    
    return Response(status_code=200)

# Also mount the messages endpoint for compatibility
app.mount("/messages", sse_transport.handle_post_message)

async def run_mcp_server(read_queue, write_queue, session_id):
    """Run the MCP server with the given queues"""
    print(f"Starting MCP server for session: {session_id}")
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
        print(f"MCP server completed normally for session: {session_id}")
    except asyncio.CancelledError:
        print(f"MCP server cancelled for session: {session_id}")
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
    try:
        while session_id in active_connections:
            # Send a ping comment every 10 seconds
            await asyncio.sleep(10)
            if session_id in active_connections:
                write_queue = active_connections[session_id]["write_queue"]
                ping_message = f": ping - {datetime.now().isoformat()}"
                await write_queue.put(ping_message)
                print(f"Sent ping to session {session_id}")
    except asyncio.CancelledError:
        print(f"Ping task cancelled for session: {session_id}")
    except Exception as e:
        print(f"Error in ping task for session {session_id}: {str(e)}")

# ============= SERVER EXECUTION =============

if __name__ == "__main__":
    print("Starting Wikidata MCP Server with SSE transport...")
    port = int(os.environ.get("PORT", 8000))
    
    # Configure uvicorn with optimized settings for Railway
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        timeout_keep_alive=300,  # Increase keep-alive timeout to 5 minutes
        log_level="info",
        proxy_headers=True,      # Enable proxy headers
        forwarded_allow_ips="*", # Allow all forwarded IPs
        workers=1                # Use a single worker for SSE
    )
