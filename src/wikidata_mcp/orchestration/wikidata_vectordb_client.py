import requests
from typing import List, Dict, Optional

class WikidataVectorDBClient:
    def __init__(self, api_key: str, base_url: str = "https://wd-vectordb.toolforge.org"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'x-api-secret': api_key,
            'Content-Type': 'application/json'
        }
    
    def search_entities(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for Wikidata entities using the vector database.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing entity information
        """
        url = f"{self.base_url}/item/query/"
        params = {
            "query": query,
            "K": limit
        }
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_entity_embedding(self, entity_id: str) -> Dict:
        """
        Get the embedding for a specific Wikidata entity.
        
        Args:
            entity_id: The Wikidata entity ID (e.g., 'Q42')
            
        Returns:
            Dictionary containing the entity's embedding
        """
        url = f"{self.base_url}/entity/{entity_id}/embedding"
        response = requests.get(
            url,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def find_similar_entities(self, entity_id: str, limit: int = 5) -> List[Dict]:
        """
        Find entities similar to the given entity using embeddings.
        
        Args:
            entity_id: The reference entity ID
            limit: Maximum number of similar entities to return
            
        Returns:
            List of dictionaries containing similar entities
        """
        url = f"{self.base_url}/similar"
        response = requests.post(
            url,
            headers=self.headers,
            json={
                "entity_id": entity_id,
                "limit": limit
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_entity_info(self, entity_id: str) -> Dict:
        """
        Get detailed information about a Wikidata entity.
        
        Args:
            entity_id: The Wikidata entity ID
            
        Returns:
            Dictionary containing entity information
        """
        url = f"{self.base_url}/entity/{entity_id}"
        response = requests.get(
            url,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
