"""
Wikidata MCP Server (SSE Version for Render)

This module implements a Model Context Protocol (MCP) server with SSE transport
that connects Large Language Models to Wikidata's structured knowledge base.
Based on the implementation pattern from ragieai/fastapi-sse-mcp.
"""
import os
import json
from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from mcp.server.sse import SseServerTransport
from mcp.server.fastmcp import FastMCP
import uvicorn

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
            return json.dumps({"error": f"No property found for '{property_name}'"})
    
    # Construct SPARQL query
    if property_id:
        sparql_query = f"""
        SELECT ?value ?valueLabel
        WHERE {{
          wd:{entity_id} wdt:{property_id} ?value.
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 10
        """
    else:
        sparql_query = f"""
        SELECT ?prop ?propLabel ?value ?valueLabel
        WHERE {{
          wd:{entity_id} ?p ?value.
          ?prop wikibase:directClaim ?p.
          
          # Filter out some common non-entity relations
          FILTER(isIRI(?value) || isLiteral(?value))
          
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

# ============= CREATE SSE SERVER =============

def create_sse_server(mcp_instance):
    """Create a Starlette app that handles SSE connections and message handling"""
    transport = SseServerTransport("/messages/")

    # Define handler functions
    async def root_handler(request):
        return {"message": "Wikidata MCP Server is running. Use /sse/ for MCP connections."}

    async def handle_sse(request):
        async with transport.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp_instance._mcp_server.run(
                streams[0], streams[1], mcp_instance._mcp_server.create_initialization_options()
            )

    # Create Starlette routes for SSE and message handling
    routes = [
        Route("/", endpoint=root_handler),
        Route("/sse/", endpoint=handle_sse),
        Mount("/messages/", app=transport.handle_post_message),
    ]

    # Create a Starlette app
    return Starlette(routes=routes)

# Create FastAPI app
app = FastAPI()

# Mount the Starlette SSE server onto the FastAPI app
app.mount("/", create_sse_server(mcp))

# ============= SERVER EXECUTION =============

if __name__ == "__main__":
    print("Starting Wikidata MCP Server with SSE transport...")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
