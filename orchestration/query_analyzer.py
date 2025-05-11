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
        Analiza una consulta en lenguaje natural y crea una seu00f1al de consulta.
        """
        # Implementaciu00f3n bu00e1sica - en una versiu00f3n real usaru00edamos NLP mu00e1s avanzado
        query_type = "generic_query"
        entities = []
        temporal_constraints = {}
        limit_constraints = None
        
        # Detectar consultas temporales
        temporal_keywords = ["último", "últimos", "primero", "primeros", "reciente", "antiguo"]
        if any(keyword in query_text.lower() for keyword in temporal_keywords):
            query_type = "temporal_query"
            
            # Intentar extraer lu00edmite numu00e9rico
            num_match = re.search(r'\b(\d+)\b', query_text)
            if num_match:
                limit_constraints = int(num_match.group(1))
        
        # Detectar entidades
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
