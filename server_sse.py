"""
Wikidata MCP Server with SSE Transport

This module implements a Model Context Protocol (MCP) server with SSE transport
that connects Large Language Models to Wikidata's structured knowledge base.
"""
import os
import json
import asyncio
import anyio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from mcp.server.sse import SseServerTransport
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from uuid import uuid4

from mcp.server.fastmcp.prompts import base
from wikidata_api import (
    search_entity,
    search_property,
    get_entity_metadata,
    get_entity_properties,
    execute_sparql
)

# Importar el sistema de orquestación para consultas complejas (condicional)
try:
    from wikidata_mcp.orchestration.mcp_integration import process_natural_language_query
    ORCHESTRATION_AVAILABLE = True
except (ImportError, ValueError) as e:
    print(f"Warning: Advanced orchestration not available: {e}")
    ORCHESTRATION_AVAILABLE = False
    def process_natural_language_query(query):
        return json.dumps({
            "error": "Advanced orchestration not available. Set WIKIDATA_VECTORDB_API_KEY environment variable.",
            "query": query,
            "success": False
        })

# Initialize FastMCP
mcp = FastMCP(name="Wikidata Knowledge")

# ============= MCP TOOLS =============

@mcp.tool()
def query_wikidata_complex(query: str) -> str:
    """
    Process complex natural language queries using Vector DB + SPARQL orchestration.
    
    ⚠️  PERFORMANCE: 1-11s latency (50x slower than basic tools for simple queries)
    ⚠️  REQUIRES: WIKIDATA_VECTORDB_API_KEY environment variable
    ✅  USE FOR: Temporal queries, complex relationships, multi-entity queries
    ❌  NEVER USE FOR: Simple entity searches, single property lookups
    
    Examples of APPROPRIATE use cases:
    - "last 3 popes" (1.3s)
    - "recent presidents of France" (1.5s)
    - "who was pope in 1978" (7.8s)
    - "Nobel Prize winners in Physics from Germany"
    
    Examples of INAPPROPRIATE use cases (use basic tools instead):
    - "Albert Einstein" (11s vs 250ms with basic tool)
    - "Paris" (9s vs 166ms with basic tool)
    
    Args:
        query: A complex natural language query requiring temporal/relational analysis
        
    Returns:
        JSON string containing the query results with metadata
    """
    try:
        result = process_natural_language_query(query)
        return result
    except Exception as e:
        return json.dumps({
            "error": f"Error processing natural language query: {str(e)}",
            "success": False,
            "query": query
        })

@mcp.tool()
def search_wikidata_entity(query: str) -> str:
    """
    ⚡ FAST: Search for a Wikidata entity by name (140-250ms average).
    
    ✅  BEST FOR: Simple entity lookups, getting QIDs for known entities
    ❌  NOT FOR: Complex queries, temporal questions, relationships
    
    PERFORMANCE: 50x faster than complex tool for simple entity searches
    
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

# Redundant function removed - using direct execute_sparql from wikidata_api
@mcp.tool("execute_wikidata_sparql")
def execute_wikidata_sparql(sparql_query: str) -> str:
    """
    ⚡ FAST: Execute SPARQL queries directly (~200ms).
    
    ✅  BEST FOR: Direct SPARQL queries when you know the exact syntax
    ❌  NOT FOR: Natural language queries (use query_wikidata_complex instead)
    
    Args:
        sparql_query: A valid SPARQL query string
        
    Returns:
        JSON string containing the query results
    """
    try:
        result = execute_sparql(sparql_query)
        return result
    except Exception as e:
        return json.dumps({
            "error": f"SPARQL execution error: {str(e)}",
            "success": False,
            "query": sparql_query
        })

# Redundant tools removed - use basic tools + execute_wikidata_sparql for custom queries

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
def position_holders_template(position_name: str, limit: int = 3) -> list[base.Message]:
    """
    Template for finding people who held a specific position, ordered by recency.
    Uses hybrid architecture for optimal performance.
    """
    return [
        base.UserMessage(f"""
You need to find the {limit} most recent holders of the position "{position_name}" in Wikidata.

🚀 HYBRID APPROACH - Choose the right tool:

**Option 1: Advanced Tool (Recommended for temporal queries)**
For queries like "recent presidents", "last 3 popes", use:
- query_wikidata_complex("{limit} most recent {position_name}")
- This handles temporal reasoning automatically (1-11s latency)

**Option 2: Basic Tools (For known positions)**
If you know the exact position ID:
1. Search for position ID: search_wikidata_property("{position_name}")
2. Execute SPARQL: execute_wikidata_sparql(query) (~200ms)

SPARQL pattern for Option 2:
```
SELECT ?person ?personLabel ?startDate WHERE {{
  ?person p:P39 [
    ps:P39 wd:Q<position_id>;  # position held: <position>
    pq:P580 ?startDate  # start time
  ].
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}} ORDER BY DESC(?startDate) LIMIT {limit}
```

⚡ Performance: Advanced tool is 50x slower for simple queries, so use basic tools when possible.
""")
    ]

@mcp.prompt()
def entity_search_template(entity_name: str) -> list[base.Message]:
    """
    Template for searching a Wikidata entity using optimized hybrid architecture.
    """
    return [
        base.UserMessage(f"""
You need to find accurate and up-to-date information about {entity_name} using Wikidata as your primary source of truth.

🚀 HYBRID ARCHITECTURE - Use the right tool for optimal performance:

**For Simple Entity Information (FAST - 140-250ms):**
1. search_wikidata_entity("{entity_name}") - Get entity ID
2. get_wikidata_metadata(entity_id) - Get labels/descriptions  
3. get_wikidata_properties(entity_id) - Get all properties
4. execute_wikidata_sparql(query) - Custom queries (~200ms)

**For Complex Queries (1-11s latency):**
Use query_wikidata_complex() ONLY for:
- Temporal queries ("recent", "last 3", "who was X in year Y")
- Complex relationships requiring multiple entities
- Natural language queries needing reasoning

❌ **NEVER use query_wikidata_complex for simple entity searches** - it's 50x slower!

**Step-by-step approach:**
1. Start with search_wikidata_entity("{entity_name}")
2. If found, use get_wikidata_metadata(entity_id) for basic info
3. Use get_wikidata_properties(entity_id) for comprehensive facts
4. For custom queries, use execute_wikidata_sparql() with SPARQL
5. Only use query_wikidata_complex() for temporal/complex relationships

**Important:** 
- Cite Wikidata as your source and include entity ID
- Use ONLY Wikidata data, not pre-trained knowledge
- If not found in Wikidata, clearly state unavailability
""")
    ]

@mcp.prompt()
def property_search_template(property_name: str) -> list[base.Message]:
    """
    Template for searching a Wikidata property using fast basic tools.
    """
    return [
        base.UserMessage(f"""
You need to find accurate information about the Wikidata property "{property_name}" using only Wikidata's data.

🚀 **USE BASIC TOOLS** - Property searches are always fast (~200ms):

**Step-by-step approach:**
1. search_wikidata_property("{property_name}") - Find property ID
2. execute_wikidata_sparql(query) - Query entities using this property
3. Check common_properties_resource for reference

**Property Search Details:**
- Property IDs start with 'P' + numbers (e.g., P31 = 'instance of')
- If not found, try alternative terms or check common_properties_resource
- Use ONLY Wikidata data, not pre-trained knowledge

**Example SPARQL pattern:**
```
SELECT ?entity ?entityLabel WHERE {{
  ?entity wdt:P31 wd:Q5.  # Find humans (Q5) using 'instance of' (P31)
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
LIMIT 10
```

**Important:**
- Replace P31 with your found property ID
- Explain what the property represents with examples
- If property not found, clearly state unavailability

⚡ **Never use query_wikidata_complex for property searches** - basic tools are sufficient and 50x faster!
""")
    ]

@mcp.prompt()
def entity_relation_template(entity1_name: str, entity2_name: str) -> list[base.Message]:
    """
    Template for finding relationships between entities using hybrid architecture.
    """
    return [
        base.UserMessage(f"""
You need to discover the factual relationships between {entity1_name} and {entity2_name} using Wikidata as your authoritative source.

🚀 **HYBRID APPROACH** - Choose based on complexity:

**Option 1: Advanced Tool (For complex relationships)**
If the relationship involves reasoning or is not straightforward:
- query_wikidata_complex("relationship between {entity1_name} and {entity2_name}")
- Handles complex reasoning automatically (1-11s latency)

**Option 2: Basic Tools (For direct relationships)**
For known entities with direct connections:

1. **Find entities (Fast - ~200ms each):**
   - search_wikidata_entity("{entity1_name}")
   - search_wikidata_entity("{entity2_name}")
   - get_wikidata_metadata(entity_id) to confirm correct entities

2. **Query relationships with SPARQL (~200ms):**
   ```
   SELECT ?relation ?relationLabel WHERE {{
     wd:[ENTITY1_ID] ?p wd:[ENTITY2_ID].
     ?property wikibase:directClaim ?p.
     BIND(?property as ?relation)
     SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
   }}
   ```

3. **For indirect relationships:**
   ```
   SELECT ?intermediateEntity ?intermediateEntityLabel ?relation1 ?relation1Label ?relation2 ?relation2Label WHERE {{
     wd:[ENTITY1_ID] ?p1 ?intermediateEntity.
     ?intermediateEntity ?p2 wd:[ENTITY2_ID].
     ?property1 wikibase:directClaim ?p1.
     ?property2 wikibase:directClaim ?p2.
     BIND(?property1 as ?relation1)
     BIND(?property2 as ?relation2)
     SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
   }} LIMIT 5
   ```

**Performance Guide:**
- Basic tools: ~600ms total for direct relationships
- Advanced tool: 1-11s for complex reasoning
- Use basic tools first, advanced only if needed

**Important:**
- Use ONLY Wikidata data, not pre-trained knowledge
- Cite sources with entity/property IDs
- If no relationship found, clearly state unavailability
""")
    ]

@mcp.prompt()
def general_wikidata_guidance() -> list[base.Message]:
    """
    General guidance for interacting with Wikidata through optimized hybrid MCP architecture.
    """
    return [
        base.UserMessage("""
When using Wikidata as a knowledge source, follow these important guidelines:

🚀 **HYBRID ARCHITECTURE - PERFORMANCE FIRST**

1. **CHOOSE THE RIGHT TOOL FOR OPTIMAL PERFORMANCE**
   ⚡ **Basic Tools (140-250ms) - USE FIRST:**
   - search_wikidata_entity: Find entity IDs by name
   - search_wikidata_property: Find property IDs by name  
   - get_wikidata_metadata: Get basic entity information
   - get_wikidata_properties: Get all properties for an entity
   - execute_wikidata_sparql: Run custom SPARQL queries
   
   🧠 **Advanced Tool (1-11s) - USE ONLY FOR:**
   - query_wikidata_complex: Temporal/complex queries requiring reasoning
   - Examples: "last 3 popes", "recent presidents", "who was X in year Y"
   - ❌ **NEVER for simple entity searches** (50x slower!)

2. **ALWAYS PREFER WIKIDATA OVER PRE-TRAINED KNOWLEDGE**
   - Wikidata contains structured, curated data that is often more accurate and up-to-date
   - Query Wikidata FIRST, fallback to pre-trained knowledge only when explicitly instructed
   - If not in Wikidata, state: "This information is not available in Wikidata"

3. **PROPERLY CITE WIKIDATA INFORMATION**
   - Always include entity ID (e.g., Q42) and property IDs (e.g., P31)
   - Format: "According to Wikidata [Q42], Douglas Adams was born on March 11, 1952 [P569]"

4. **LEVERAGE AVAILABLE RESOURCES**
   - common_properties_resource: Reference for commonly used property IDs
   - sparql_examples_resource: Example SPARQL queries for common tasks

5. **CRAFT EFFECTIVE SPARQL QUERIES**
   - Use proper prefixes (wdt:, wd:, p:, ps:, etc.)
   - Include label service for human-readable results
   - Limit results appropriately to avoid overwhelming responses

6. **PERFORMANCE OPTIMIZATION PATTERNS**
   - Simple entity info: Basic tools (~200ms total)
   - Complex temporal queries: Advanced tool (1-11s)
   - Direct relationships: SPARQL with basic tools (~200ms)
   - Multi-step reasoning: Advanced tool only

7. **COMMON QUERY PATTERNS (Use with basic tools)**
   - List of people with a position: ?person wdt:P39 wd:Q<position_id>
   - Current holders: Add filters for end date or lack thereof
   - Last N holders: ORDER BY DESC(?startDate) LIMIT N
   - Temporal relationships: Use pq:P580 (start time) and pq:P582 (end time)

8. **EXAMPLE SPARQL PATTERNS (Use with execute_wikidata_sparql):**
   - Last 3 popes (⚡ Basic tool ~200ms vs 🧠 Advanced tool 1.3s):
     ```
     SELECT ?pope ?popeLabel ?startDate WHERE {
       ?pope p:P39 [
         ps:P39 wd:Q19546;  # position held: pope
         pq:P580 ?startDate  # start time
       ].
       SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
     } ORDER BY DESC(?startDate) LIMIT 3
     ```
   
   - Current heads of state:
     ```
     SELECT ?person ?personLabel ?country ?countryLabel WHERE {
       ?country wdt:P31 wd:Q6256.  # instance of: country
       ?person p:P39 [
         ps:P39 ?position;
         pq:P580 ?start
       ].
       ?position wdt:P279* wd:Q48352.  # subclass of: head of state
       FILTER NOT EXISTS { ?person p:P39/pq:P582 ?end }  # No end date
       SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
     }
     ```

🎯 **PERFORMANCE SUMMARY:**
- Simple queries: Use basic tools (50x faster)
- Complex reasoning: Use advanced tool (when needed)
- Always start with basic tools, escalate only if necessary

By following these guidelines, you'll provide accurate, up-to-date, and performant Wikidata interactions.
""")
    ]

# ============= CREATE SSE APP =============

# Configure SSE transport with trailing slash to match client expectations
sse_transport = SseServerTransport("/messages/")  

# Create FastAPI app with explicit CORS configuration
app = FastAPI()

# Add CORS middleware with explicit CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Almacenar sesiones activas
active_sessions = {}

# Define root endpoint
@app.get("/")
def root():
    return {"message": "Wikidata MCP Server is running. Use /sse for MCP connections."}

# Health check endpoint for Render
@app.get("/health")
def health():
    return {"status": "healthy", "connections": len(active_sessions)}

# Define SSE endpoint
@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP connections"""
    client_host = request.client.host if hasattr(request, 'client') and request.client else 'unknown'
    print(f"SSE connection request received from: {client_host}")
    
    # Check if there's a session ID in the query parameters
    existing_session_id = request.query_params.get("session_id")
    
    # If a valid session ID was provided and exists, use it
    if existing_session_id and existing_session_id in active_sessions:
        session_id = existing_session_id
        print(f"Using existing session ID: {session_id}")
        # Update the last activity timestamp
        active_sessions[session_id]["last_activity"] = datetime.now().isoformat()
    else:
        # Generate a new session ID for this connection
        session_id = str(uuid4())
        print(f"Generated new session ID: {session_id}")
        
        # Store the session with more metadata
        active_sessions[session_id] = {
            "client_host": client_host,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "connection_count": 1
        }
    print(f"Active sessions: {len(active_sessions)}")
    
    # Use the standard SseServerTransport approach
    async with sse_transport.connect_sse(
        request.scope,
        request.receive,
        request._send,  # noqa: SLF001
    ) as (read_stream, write_stream):
        # Create timeout options with extended timeout
        timeout_options = {"timeoutMs": 600000}  # 10 minutes
        
        print(f"Starting MCP server with session ID: {session_id}")
        try:
            # Add a small delay to ensure connection is fully established
            await asyncio.sleep(0.5)
            
            # Use default initialization options without any modifications
            init_options = mcp._mcp_server.create_initialization_options()
            
            # Run MCP server with default initialization options
            await mcp._mcp_server.run(
                read_stream,
                write_stream,
                init_options
            )
        except RuntimeError as re:
            error_msg = str(re)
            print(f"RuntimeError in MCP server: {error_msg}")
            # Provide more detailed error message for initialization issues
            if "initialization was complete" in error_msg:
                print(f"Initialization error for session {session_id}. Client may have sent requests too early.")
            # Eliminar la sesión si hay un error
            if session_id in active_sessions:
                del active_sessions[session_id]
            # Don't re-raise the exception to prevent 500 errors
            return Response(status_code=503, content="Service temporarily unavailable. Please try again.")
        except Exception as e:
            print(f"Error in MCP server: {e}")
            # Eliminar la sesión si hay un error
            if session_id in active_sessions:
                del active_sessions[session_id]
            # Don't re-raise the exception to prevent 500 errors
            return Response(status_code=500, content="Internal server error. Please try again later.")
        finally:
            # Eliminar la sesión cuando se cierra la conexión
            if session_id in active_sessions:
                del active_sessions[session_id]
            print(f"SSE connection closed for session {session_id}")

# Añadir un endpoint OPTIONS explícito para /messages y /messages/
@app.options("/messages")
@app.options("/messages/")
async def options_messages():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Añadir un endpoint POST explícito para /messages (sin barra final)
@app.post("/messages")
async def post_messages_no_slash(request: Request):
    """Handle POST requests to /messages endpoint (no trailing slash)"""
    client_host = request.client.host if hasattr(request, 'client') and request.client else 'unknown'
    print(f"POST request to /messages received from: {client_host}")
    
    try:
        # Extract the session_id from query parameters
        session_id = request.query_params.get("session_id")
        print(f"Session ID from query params: {session_id}")
        
        # Verify if the session is active
        if not session_id or session_id not in active_sessions:
            print(f"Session ID {session_id} not found in active sessions")
            # If we have any active sessions, use the most recently active one
            if active_sessions:
                # Sort sessions by last_activity if available
                sorted_sessions = sorted(
                    active_sessions.items(),
                    key=lambda x: x[1].get("last_activity", x[1].get("created_at", "")),
                    reverse=True
                )
                session_id = sorted_sessions[0][0]
                print(f"Using most recent active session: {session_id}")
                # Update session metadata
                active_sessions[session_id]["last_activity"] = datetime.now().isoformat()
                active_sessions[session_id]["message_count"] = active_sessions[session_id].get("message_count", 0) + 1
            else:
                # If no active sessions exist, create a new one
                session_id = str(uuid4())
                print(f"No active sessions found, generated new session ID: {session_id}")
                active_sessions[session_id] = {
                    "client_host": client_host,
                    "created_at": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat(),
                    "message_count": 1,
                    "connection_count": 0  # Will be incremented when SSE connection is established
                }
        else:
            # Update session metadata for existing session
            active_sessions[session_id]["last_activity"] = datetime.now().isoformat()
            active_sessions[session_id]["message_count"] = active_sessions[session_id].get("message_count", 0) + 1
        
        # Add session_id to query params if not present
        if "session_id" not in request.query_params:
            # Create a new request with the session_id added
            # This is a bit hacky but necessary since FastAPI request objects are immutable
            request.scope["query_string"] = f"session_id={session_id}".encode()
        
        # Print request body for debugging (limited to first 200 chars)
        body = await request.body()
        body_str = body.decode('utf-8')[:200]
        print(f"Request body (truncated): {body_str}...")
        
        # Use the SseServerTransport's handle_post_message method
        try:
            # Add a small delay to ensure the SSE connection is ready
            await asyncio.sleep(0.5)
            
            # Handle the message with error catching
            response = await sse_transport.handle_post_message(request)
            return response
        except anyio.BrokenResourceError:
            # This is a common error when the client disconnects or the stream is broken
            print(f"BrokenResourceError for session {session_id} - client may have disconnected")
            return Response(
                status_code=202,  # Accepted but not processed
                content="Message received but connection was broken. Please reconnect SSE.",
                media_type="text/plain"
            )
        except Exception as e:
            print(f"Error in handle_post_message: {e}")
            return Response(
                status_code=500,
                content=f"Error processing request: {str(e)}",
                media_type="text/plain"
            )
    except Exception as e:
        print(f"Error handling POST request: {e}")
        return Response(
            status_code=500,
            content=f"Error processing request: {str(e)}",
            media_type="text/plain"
        )

# Mount the messages endpoint with trailing slash for handling POST requests
app.mount("/messages/", app=sse_transport.handle_post_message)

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
