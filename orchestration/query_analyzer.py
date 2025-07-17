import json
import os
import re
import datetime
from typing import Dict, List, Optional, Any
from .query_signals import QuerySignal

class QueryAnalyzer:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "wikidata_config.json"
        )
        with open(self.config_path, "r") as f:
            self.config = json.load(f)
    
    def analyze(self, query_text: str, current_date: datetime.date = None, vector_entities: Optional[List[Dict]] = None) -> QuerySignal:
        """
        Analyzes a natural language query and creates a query signal.
        
        Args:
            query_text: The natural language query text
            current_date: Optional current date for temporal context (defaults to today)
        
        Returns:
            A QuerySignal object representing the analyzed query
        """
        # Use the provided date or default to today
        current_date = current_date or datetime.date.today()
        
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
        
        # Detect entities from vector search results
        if vector_entities:
            for entity in vector_entities:
                entity_id = entity.get('id') or entity.get('entity_id')
                if entity_id and entity_id not in entities:
                    entities.append(entity_id)

        # Fallback to keyword-based entity detection
        for entity_name, entity_id in self.config.get("commonEntities", {}).items():
            if entity_name in query_text.lower() and entity_id not in entities:
                entities.append(entity_id)
        
        return QuerySignal(
            query_type=query_type,
            entities=entities,
            temporal_constraints=temporal_constraints,
            limit_constraints=limit_constraints,
            message=f"Query: {query_text}",
            current_date=current_date
        )
