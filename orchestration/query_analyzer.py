import json
import os
import re
from typing import Dict, List, Optional, Any
from .query_signals import QuerySignal

class QueryAnalyzer:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "wikidata_config.json"
        )
        with open(self.config_path, "r") as f:
            self.config = json.load(f)
    
    def analyze(self, query_text: str) -> QuerySignal:
        """
        Analyzes a natural language query and creates a query signal.
        """
        # Basic implementation - in a real version we would use more advanced NLP
        query_type = "generic_query"
        entities = []
        temporal_constraints = {}
        limit_constraints = None
        
        # Detect temporal queries
        temporal_keywords = ["last", "latest", "first", "recent", "oldest", "newest", "current"]
        if any(keyword in query_text.lower() for keyword in temporal_keywords):
            query_type = "temporal_query"
            
            # Try to extract numeric limit
            num_match = re.search(r'\b(\d+)\b', query_text)
            if num_match:
                limit_constraints = int(num_match.group(1))
        
        # Detect entities
        for entity_name, entity_id in self.config.get("commonEntities", {}).items():
            if entity_name in query_text.lower():
                entities.append(entity_id)
        
        return QuerySignal(
            query_type=query_type,
            entities=entities,
            temporal_constraints=temporal_constraints,
            limit_constraints=limit_constraints,
            message=f"Consulta: {query_text}"
        )
