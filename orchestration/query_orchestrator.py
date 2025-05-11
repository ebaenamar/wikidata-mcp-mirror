import json
import os
from typing import Dict, Any
from .query_analyzer import QueryAnalyzer
from .temporal_specialist import TemporalSpecialist
from .query_signals import QuerySignal
from .wikidata_cache import WikidataCache

class QueryOrchestrator:
    def __init__(self, config_path: str = None, use_cache: bool = True):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "wikidata_config.json"
        )
        self.analyzer = QueryAnalyzer(self.config_path)
        self.temporal_specialist = TemporalSpecialist(self.config_path)
        
        # Inicializar el sistema de caché
        self.use_cache = use_cache
        if use_cache:
            self.cache = WikidataCache()
        
        # Registrar especialistas
        self.specialists = {
            "temporal_query": self.temporal_specialist.handle_query
        }
    
    def process_query(self, query_text: str) -> Dict[str, Any]:
        """
        Procesa una consulta en lenguaje natural y devuelve los resultados.
        Utiliza el sistema de caché si está habilitado.
        """
        # Verificar si hay resultados en caché
        if self.use_cache:
            cached_result = self.cache.get(query_text)
            if cached_result:
                return cached_result
        
        # Analizar la consulta para crear una señal
        signal = self.analyzer.analyze(query_text)
        
        # Delegar a un especialista según el tipo de consulta
        result = None
        if signal.query_type in self.specialists:
            result = self.specialists[signal.query_type](signal)
        else:
            # Consulta genérica si no hay un especialista
            result = self._handle_generic_query(signal)
        
        # Guardar el resultado en caché
        if self.use_cache and result:
            self.cache.set(query_text, result)
            
        return result
    
    def _handle_generic_query(self, signal: QuerySignal) -> Dict[str, Any]:
        """
        Handles generic queries that don't fit into other categories.
        """
        return {
            "warning": "Non-specialized query",
            "query_type": signal.query_type,
            "message": signal.message
        }
