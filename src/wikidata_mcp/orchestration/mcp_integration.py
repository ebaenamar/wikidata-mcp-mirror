import json
import datetime
from typing import Dict, Any, Optional
from .query_orchestrator import QueryOrchestrator
from .query_feedback import QueryFeedback

# Inicializar el orquestador de consultas y el sistema de feedback
orchestrator = QueryOrchestrator(use_feedback=True)
feedback_system = QueryFeedback()

def process_natural_language_query(query_text: str, current_date: Optional[datetime.date] = None) -> str:
    """
    Processes a natural language query and returns the results as JSON.
    
    Args:
        query_text: The natural language query text
        current_date: Optional current date for temporal context (defaults to today)
        
    Returns:
        A JSON string containing the query results with temporal context
    """
    try:
        # Use the provided date or default to today
        current_date = current_date or datetime.date.today()
        
        # Pass the current date to the orchestrator
        results = orchestrator.process_query(query_text, current_date)
        
        # Add current date information to the response if not already present
        if isinstance(results, dict) and "metadata" not in results:
            results["metadata"] = {
                "current_date": current_date.isoformat(),
                "query_processed_on": datetime.datetime.now().isoformat()
            }
            
        return json.dumps(results)
    except Exception as e:
        error_message = f"Error processing query: {str(e)}"
        error_result = {
            "error": error_message,
            "metadata": {
                "current_date": current_date.isoformat() if current_date else datetime.date.today().isoformat(),
                "query_processed_on": datetime.datetime.now().isoformat()
            }
        }
        return json.dumps(error_result)
