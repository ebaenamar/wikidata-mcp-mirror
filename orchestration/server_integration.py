"""
Este módulo contiene las modificaciones necesarias para integrar el orquestador
de consultas con el servidor MCP existente.

Instrucciones de integración:
1. Importar este módulo en server_sse.py
2. Modificar la función execute_wikidata_sparql para usar process_natural_language_query
   cuando la consulta no sea SPARQL directa.
"""

import json
from .mcp_integration import process_natural_language_query

def is_sparql_query(query: str) -> bool:
    """
    Determina si una consulta es SPARQL o lenguaje natural.
    """
    query = query.strip().upper()
    return (query.startswith("SELECT") or 
            query.startswith("CONSTRUCT") or 
            query.startswith("ASK") or 
            query.startswith("DESCRIBE"))

def enhanced_execute_wikidata_sparql(original_function):
    """
    Decorador que mejora la función execute_wikidata_sparql para manejar
    consultas en lenguaje natural.
    """
    def wrapper(sparql_query: str) -> str:
        try:
            # Si es una consulta SPARQL directa, ejecutarla normalmente
            if is_sparql_query(sparql_query):
                return original_function(sparql_query)
            
            # Si no es SPARQL, procesarla como lenguaje natural
            return process_natural_language_query(sparql_query)
        except Exception as e:
            error_message = f"Error al ejecutar la consulta: {str(e)}"
            return json.dumps({"error": error_message})
    
    return wrapper
