"""
Wikidata MCP Server with FastMCP SSE Transport

This module implements a Model Context Protocol (MCP) server using FastMCP's
built-in SSE transport that connects Large Language Models to Wikidata's 
structured knowledge base.
"""
import os
from mcp.server.fastmcp import FastMCP
from datetime import datetime

# Import all the MCP tools and prompts from the existing modules
from mcp.server.fastmcp.prompts import base
from wikidata_api import (
    search_entity,
    search_property, 
    get_entity_metadata,
    get_entity_properties,
    execute_sparql
)

# Try to import advanced orchestration (optional)
try:
    from src.wikidata_mcp.orchestration.query_orchestrator import QueryOrchestrator
    # Initialize the orchestrator
    orchestrator = QueryOrchestrator()
    ORCHESTRATION_AVAILABLE = True
    print("Advanced orchestration available")
except ImportError as e:
    ORCHESTRATION_AVAILABLE = False
    print(f"Warning: Advanced orchestration not available: {e}")

# Initialize FastMCP
mcp = FastMCP(name="Wikidata Knowledge")

# ============= MCP TOOLS =============

@mcp.tool()
def search_wikidata_entity(query: str) -> str:
    """Search for Wikidata entities by name or description."""
    return search_entity(query)

@mcp.tool()
def search_wikidata_property(query: str) -> str:
    """Search for Wikidata properties by name or description."""
    return search_property(query)

@mcp.tool()
def get_wikidata_metadata(entity_id: str) -> dict:
    """Get detailed metadata for a Wikidata entity."""
    return get_entity_metadata(entity_id)

@mcp.tool()
def get_wikidata_properties(entity_id: str) -> dict:
    """Get all properties and their values for a Wikidata entity."""
    return get_entity_properties(entity_id)

@mcp.tool()
def execute_wikidata_sparql(query: str) -> dict:
    """Execute a SPARQL query against Wikidata."""
    return execute_sparql(query)

# Add advanced tool only if orchestration is available
if ORCHESTRATION_AVAILABLE:
    @mcp.tool()
    def query_wikidata_complex(query: str) -> dict:
        """Advanced Wikidata query with vector database and LLM orchestration."""
        return orchestrator.process_query(query)

# ============= MCP PROMPTS =============

@mcp.prompt()
def entity_search_template() -> str:
    """Template for searching Wikidata entities efficiently."""
    return """
# Wikidata Entity Search Guide

## Performance-First Approach
- **Basic tools** (search_wikidata_entity, get_wikidata_metadata): ~200ms ⚡
- **Advanced tool** (query_wikidata_complex): 1-11s 🐌
- **Speed difference**: Basic tools are 50x faster!

## Search Strategy
1. **Start with basic search**: Use `search_wikidata_entity` for initial discovery
2. **Get details**: Use `get_wikidata_metadata` for entity information  
3. **Advanced only when needed**: Use `query_wikidata_complex` for complex relationships

## Example Workflow
```
User: "Find information about Marie Curie"
1. search_wikidata_entity("Marie Curie") → Q7186
2. get_wikidata_metadata("Q7186") → Full details
```

Always prefer basic tools for simple queries!
"""

@mcp.prompt()
def general_wikidata_guidance() -> str:
    """General guidance for using Wikidata MCP tools effectively."""
    return """
# Wikidata MCP Server - Performance Guide

## 🚀 Tool Performance Hierarchy

### ⚡ FAST Tools (140-250ms) - Use First
- `search_wikidata_entity`: Find entities by name
- `search_wikidata_property`: Find properties by name  
- `get_wikidata_metadata`: Get entity details
- `get_wikidata_properties`: Get all entity properties
- `execute_wikidata_sparql`: Run SPARQL queries

### 🐌 SLOW Tool (1-11s) - Use Sparingly
- `query_wikidata_complex`: Advanced reasoning with vector DB

## 📋 Usage Guidelines

### ✅ RIGHT Tool for the Job
- **Simple lookups**: Basic tools (50x faster!)
- **Known entities**: Basic tools
- **Complex temporal queries**: Advanced tool
- **Multi-step reasoning**: Advanced tool

### ❌ WRONG Usage Patterns
- Using advanced tool for simple entity lookups
- Using advanced tool when you know the entity ID
- Using advanced tool for basic property searches

## 🎯 Performance Tips
1. **Always start with basic tools**
2. **Use advanced tool only for complex reasoning**
3. **Cache entity IDs when possible**
4. **Prefer SPARQL for structured queries**

By following these guidelines, you'll provide accurate, up-to-date, and performant Wikidata interactions.
"""

# ============= MCP RESOURCES =============

@mcp.resource("wikidata://common-properties")
def common_properties_resource() -> str:
    """Common Wikidata properties for reference."""
    return """
# Common Wikidata Properties

## Basic Properties
- P31: instance of
- P279: subclass of  
- P106: occupation
- P27: country of citizenship
- P19: place of birth
- P20: place of death
- P569: date of birth
- P570: date of death

## Relationships
- P22: father
- P25: mother
- P26: spouse
- P40: child
- P3373: sibling

## Locations
- P17: country
- P131: located in administrative territorial entity
- P625: coordinate location

## Works & Achievements
- P800: notable work
- P166: award received
- P69: educated at
- P108: employer
"""

# ============= SERVER EXECUTION =============

if __name__ == "__main__":
    print("Starting Wikidata MCP Server with FastMCP SSE transport...")
    
    # Use FastMCP's built-in SSE transport
    # Explicitly bind to all network interfaces for container deployment
    import os
    host = '0.0.0.0'  # Always bind to all interfaces for Render
    port = int(os.getenv('PORT', '8000'))  # Use PORT from environment or default to 8000
    
    print(f"Starting server on {host}:{port}")
    print(f"Environment: PORT={port}, HOST={host}")
    
    # Start the server with explicit host and port binding
    # Using FastMCP v2 configuration for SSE transport
    mcp.run(
        transport="sse",
        transport_config={
            "host": host,
            "port": port
        },
        log_level="info"
    )
