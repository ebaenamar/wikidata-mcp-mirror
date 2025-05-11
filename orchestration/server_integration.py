"""
This module contains the necessary modifications to integrate the query orchestrator
with the existing MCP server.

Integration instructions:
1. Import this module in server_sse.py
2. Modify the execute_wikidata_sparql function to use process_natural_language_query
   when the query is not direct SPARQL.
"""

import json
from .mcp_integration import process_natural_language_query

def is_sparql_query(query: str) -> bool:
    """
    Determines if a query is SPARQL or natural language.
    """
    query = query.strip().upper()
    return (query.startswith("SELECT") or 
            query.startswith("CONSTRUCT") or 
            query.startswith("ASK") or 
            query.startswith("DESCRIBE"))

def enhanced_execute_wikidata_sparql(original_function):
    """
    Decorator that enhances the execute_wikidata_sparql function to handle
    natural language queries.
    """
    def wrapper(sparql_query: str) -> str:
        try:
            # If it's a direct SPARQL query, execute it normally
            if is_sparql_query(sparql_query):
                return original_function(sparql_query)
            
            # If it's not SPARQL, process it as natural language
            return process_natural_language_query(sparql_query)
        except Exception as e:
            error_message = f"Error executing query: {str(e)}"
            return json.dumps({"error": error_message})
    
    return wrapper
