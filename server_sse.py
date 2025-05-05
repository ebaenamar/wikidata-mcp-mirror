"""
Wikidata MCP Server (SSE Version)

This module implements a Model Context Protocol (MCP) server with SSE transport
that connects Large Language Models to Wikidata's structured knowledge base.
"""
import json
import asyncio
from typing import Optional, List, Dict, Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from mcp.server.sse import create_sse_app
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

# Create an ASGI application with SSE support
app = create_sse_app(mcp)

# ============= SERVER EXECUTION =============

# For Render deployment - this is the entry point
if __name__ == "__main__":
    print("Starting Wikidata MCP Server with SSE transport...")
    import os
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
