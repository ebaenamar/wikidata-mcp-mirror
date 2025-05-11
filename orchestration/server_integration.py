"""
This module contains the necessary modifications to integrate the query orchestrator
with the existing MCP server.

Integration instructions:
1. Import this module in server_sse.py
2. Modify the execute_wikidata_sparql function to use process_natural_language_query
   when the query is not direct SPARQL.
"""

import json
import datetime
from typing import Optional
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
    
    Args:
        original_function: The original execute_wikidata_sparql function to enhance
        
    Returns:
        A wrapper function that handles both SPARQL and natural language queries
    """
    def wrapper(sparql_query: str, current_date: Optional[datetime.date] = None) -> str:
        try:
            # Use the provided date or default to today
            current_date = current_date or datetime.date.today()
            
            # If it's a direct SPARQL query, execute it normally
            if is_sparql_query(sparql_query):
                result = original_function(sparql_query)
                
                # Try to add metadata to SPARQL results if it's JSON
                try:
                    result_data = json.loads(result)
                    if isinstance(result_data, dict) and "metadata" not in result_data:
                        result_data["metadata"] = {
                            "current_date": current_date.isoformat(),
                            "query_processed_on": datetime.datetime.now().isoformat(),
                            "query_type": "sparql"
                        }
                        return json.dumps(result_data)
                except:
                    # If we can't parse as JSON, return the original result
                    pass
                    
                return result
            
            # If it's not SPARQL, process it as natural language with current date context
            return process_natural_language_query(sparql_query, current_date)
        except Exception as e:
            error_message = f"Error executing query: {str(e)}"
            error_result = {
                "error": error_message,
                "metadata": {
                    "current_date": current_date.isoformat() if current_date else datetime.date.today().isoformat(),
                    "query_processed_on": datetime.datetime.now().isoformat()
                }
            }
            return json.dumps(error_result)
    
    return wrapper
