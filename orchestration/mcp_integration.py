import json
from typing import Dict, Any
from .query_orchestrator import QueryOrchestrator

# Inicializar el orquestador de consultas
orchestrator = QueryOrchestrator()

def process_natural_language_query(query_text: str) -> str:
    """
    Procesa una consulta en lenguaje natural y devuelve los resultados como JSON.
    """
    try:
        results = orchestrator.process_query(query_text)
        return json.dumps(results)
    except Exception as e:
        error_message = f"Error al procesar la consulta: {str(e)}"
        return json.dumps({"error": error_message})
