import json
import os
import datetime
from typing import Dict, Any, Optional
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
    
    def process_query(self, query_text: str, current_date: Optional[datetime.date] = None) -> Dict[str, Any]:
        """
        Processes a natural language query and returns the results.
        Uses the cache system if enabled.
        
        Args:
            query_text: The natural language query text
            current_date: Optional current date for temporal context (defaults to today)
            
        Returns:
            A dictionary containing the query results with temporal context
        """
        # Use the provided date or default to today
        current_date = current_date or datetime.date.today()
        
        # Check if there are cached results
        if self.use_cache:
            cached_result = self.cache.get(query_text)
            if cached_result:
                # Add current date metadata to cached results if not present
                if isinstance(cached_result, dict) and "metadata" not in cached_result:
                    cached_result["metadata"] = {
                        "current_date": current_date.isoformat(),
                        "query_processed_on": datetime.datetime.now().isoformat(),
                        "source": "cache"
                    }
                return cached_result
        
        # Analyze the query to create a signal with current date context
        signal = self.analyzer.analyze(query_text, current_date)
        
        # Delegate to a specialist based on the query type
        result = None
        if signal.query_type in self.specialists:
            result = self.specialists[signal.query_type](signal)
        else:
            # Generic query if there is no specialist
            result = self._handle_generic_query(signal)
        
        # Save the result in cache
        if self.use_cache and result:
            self.cache.set(query_text, result)
            
        return result
    
    def _handle_generic_query(self, signal: QuerySignal) -> Dict[str, Any]:
        """
        Handles generic queries that don't fit into other categories.
        
        Args:
            signal: The query signal containing the analyzed query information
            
        Returns:
            A dictionary with a warning message and metadata
        """
        # Get the current date from the signal for temporal context
        current_date = signal.current_date
        current_date_str = current_date.isoformat()
        
        return {
            "warning": "Non-specialized query",
            "query_type": signal.query_type,
            "message": signal.message,
            "metadata": {
                "current_date": current_date_str,
                "query_processed_on": datetime.datetime.now().isoformat()
            }
        }
