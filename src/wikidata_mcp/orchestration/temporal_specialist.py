import json
import os
import datetime
from typing import Dict, Any, Optional
from .query_signals import QuerySignal
from .sparql_executor import create_sparql_executor

class TemporalSpecialist:
    def __init__(self, config_path: str = None, sparql_executor=None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "wikidata_config.json"
        )
        with open(self.config_path, "r") as f:
            self.config = json.load(f)
        
        # Use the provided executor or create a real SPARQL executor
        if sparql_executor is None:
            # Create a real SPARQL executor for Wikidata
            self.sparql_executor = create_sparql_executor()
            self.execute_sparql = self.sparql_executor.execute_query
        else:
            self.execute_sparql = sparql_executor
    
    def handle_query(self, signal: QuerySignal) -> Dict[str, Any]:
        """
        Handles queries with temporal constraints using a generic approach.
        
        Args:
            signal: The query signal containing the analyzed query information
            
        Returns:
            A dictionary with the query results
        """
        current_date_str = datetime.date.today().isoformat()
        
        # Add metadata about when the query was processed
        result_metadata = {
            "metadata": {
                "current_date": current_date_str,
                "query_processed_on": datetime.datetime.now().isoformat()
            }
        }
        
        # Generic temporal query handler
        if signal.entities:
            # First, try to detect position keywords in the query
            position_entity = self._detect_position_from_keywords(signal.message)
            if position_entity:
                try:
                    result = self._handle_position_query(position_entity, signal, result_metadata)
                    if result.get('success'):
                        return result
                except Exception as e:
                    pass
            
            # Try to find position-based queries for the entities
            for entity in signal.entities:
                try:
                    result = self._handle_position_query(entity, signal, result_metadata)
                    if result.get('success'):
                        return result
                except Exception as e:
                    continue  # Try next entity
            
            # If no position-based query worked, try general entity queries
            try:
                result = self._handle_general_entity_query(signal, result_metadata)
                if result.get('success'):
                    return result
            except Exception as e:
                pass
        
        # Fallback: generic error
        error_result = {
            "error": "Could not process temporal query",
            "success": False,
            "entities_searched": signal.entities,
            "query_type": "temporal_query_failed"
        }
        error_result.update(result_metadata)
        return error_result
    
    def _handle_position_query(self, entity: str, signal: QuerySignal, result_metadata: dict) -> Dict[str, Any]:
        """
        Try to handle the entity as a position (like Pope, President, etc.)
        """
        limit_clause = f"LIMIT {signal.limit_constraints}" if signal.limit_constraints else "LIMIT 10"
        
        # Generic SPARQL query for position holders
        sparql = f"""
        SELECT ?person ?personLabel ?startTime ?endTime WHERE {{
          ?person wdt:P31 wd:Q5 ;  # Instance of: human
                  p:P39 [ ps:P39 wd:{entity} ; pq:P580 ?startTime ] .  # Position held with start time
          OPTIONAL {{ ?person p:P39 [ ps:P39 wd:{entity} ; pq:P582 ?endTime ] }}  # Optional end time
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
        }}
        ORDER BY DESC(?startTime)
        {limit_clause}
        """
        
        result = self.execute_sparql(sparql)
        
        if isinstance(result, dict) and result.get('success') and result.get('count', 0) > 0:
            # Transform results
            people = []
            for person_data in result.get('results', []):
                people.append({
                    'entity': person_data.get('person'),
                    'label': person_data.get('personLabel'),
                    'startTime': person_data.get('startTime'),
                    'endTime': person_data.get('endTime')
                })
            
            response = {
                'success': True,
                'results': people,
                'count': len(people),
                'query_type': 'temporal_position_query',
                'position_entity': entity
            }
            response.update(result_metadata)
            return response
        
        return {'success': False}
    
    def _handle_general_entity_query(self, signal: QuerySignal, result_metadata: dict) -> Dict[str, Any]:
        """
        Handle general entity queries (like Nobel Prize winners, etc.)
        """
        limit_clause = f"LIMIT {signal.limit_constraints}" if signal.limit_constraints else "LIMIT 10"
        
        # Try to find recent instances or recipients of the entities
        entities_str = ' '.join([f'wd:{entity}' for entity in signal.entities[:3]])  # Limit to first 3 entities
        
        sparql = f"""
        SELECT DISTINCT ?item ?itemLabel ?date WHERE {{
          {{
            # Try as award/prize recipients
            ?item wdt:P166 ?award .
            ?award wdt:P31*/wdt:P279* ?type .
            VALUES ?type {{ {entities_str} }}
            OPTIONAL {{ ?item p:P166 [ ps:P166 ?award ; pq:P585 ?date ] }}
          }} UNION {{
            # Try as instances with point in time
            ?item wdt:P31*/wdt:P279* ?type .
            VALUES ?type {{ {entities_str} }}
            OPTIONAL {{ ?item wdt:P585 ?date }}
          }} UNION {{
            # Try as events or occurrences
            ?item wdt:P31 ?type .
            VALUES ?type {{ {entities_str} }}
            OPTIONAL {{ ?item wdt:P580 ?date }}  # Start time
          }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
        }}
        ORDER BY DESC(?date)
        {limit_clause}
        """
        
        result = self.execute_sparql(sparql)
        
        if isinstance(result, dict) and result.get('success') and result.get('count', 0) > 0:
            # Transform results
            items = []
            for item_data in result.get('results', []):
                items.append({
                    'entity': item_data.get('item'),
                    'label': item_data.get('itemLabel'),
                    'date': item_data.get('date')
                })
            
            response = {
                'success': True,
                'results': items,
                'count': len(items),
                'query_type': 'temporal_general_query',
                'searched_entities': signal.entities
            }
            response.update(result_metadata)
            return response
        
        return {'success': False}
    
    def _detect_position_from_keywords(self, query_text: str) -> Optional[str]:
        """
        Detect position entities from keywords in the query text
        """
        query_lower = query_text.lower()
        keyword_to_position = self.config.get('keywordToPosition', {})
        
        # Check for exact keyword matches (longer phrases first)
        keywords_by_length = sorted(keyword_to_position.keys(), key=len, reverse=True)
        
        for keyword in keywords_by_length:
            if keyword in query_lower:
                return keyword_to_position[keyword]
        
        return None
