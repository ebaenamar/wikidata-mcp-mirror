import json
import os
import datetime
from typing import Dict, Any, Optional
from .query_signals import QuerySignal

class TemporalSpecialist:
    def __init__(self, config_path: str = None, sparql_executor=None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "wikidata_config.json"
        )
        with open(self.config_path, "r") as f:
            self.config = json.load(f)
        
        # Use the provided executor or create a dummy function for tests
        if sparql_executor is None:
            # In a real environment, we would import wikidata_api.execute_sparql
            # But for tests, we use a dummy function that returns an error
            self.execute_sparql = lambda query: '{"error": "No real SPARQL executor was provided"}'
        else:
            self.execute_sparql = sparql_executor
    
    def handle_query(self, signal: QuerySignal) -> Dict[str, Any]:
        """
        Handles queries with temporal constraints.
        
        Args:
            signal: The query signal containing the analyzed query information
            
        Returns:
            A dictionary with the query results
        """
        # Get the current date from the signal for temporal context
        current_date = signal.current_date
        current_date_str = current_date.isoformat()
        
        # Add current date information to the response
        result_metadata = {
            "metadata": {
                "current_date": current_date_str,
                "query_processed_on": datetime.datetime.now().isoformat()
            }
        }
        
        # Example: "last 3 popes"
        if "Q9951" in signal.entities and signal.limit_constraints:  # Pope
            # Choose the appropriate template based on the query type
            if "current" in signal.message.lower():
                pattern = self.config["queryPatterns"]["current_position_holders"]
                sparql = pattern["sparqlTemplate"].format(
                    position="Q9951",  # Pope
                    limit=signal.limit_constraints,
                    current_date=current_date_str
                )
            else:
                pattern = self.config["queryPatterns"]["last_n_position_holders"]
                sparql = pattern["sparqlTemplate"].format(
                    position="Q9951",  # Pope
                    limit=signal.limit_constraints
                )
                
                # Add a filter to exclude future dates based on current date
                sparql = sparql.replace("ORDER BY DESC(?startDate)", 
                                     f"FILTER(?startDate <= \"{current_date_str}\"^^xsd:date) " + 
                                     "ORDER BY DESC(?startDate)")
            try:
                result = self.execute_sparql(sparql)
                result_data = json.loads(result) if isinstance(result, str) else result
                
                # Add the current date metadata to the result
                if isinstance(result_data, dict):
                    result_data.update(result_metadata)
                
                return result_data
            except Exception as e:
                error_result = {"error": f"Error executing SPARQL query: {str(e)}"}
                error_result.update(result_metadata)
                return error_result
        
        # Implement more cases...
        error_result = {"error": "Could not process temporal query"}
        error_result.update(result_metadata)
        return error_result
