"""
SPARQL executor for Wikidata queries.
"""
import requests
import json
import time
from typing import Dict, Any, Optional

class WikidataSPARQLExecutor:
    """
    Executes SPARQL queries against the Wikidata Query Service.
    """
    
    def __init__(self, endpoint: str = "https://query.wikidata.org/sparql", 
                 user_agent: str = "WikidataMCP/1.0 (https://github.com/your-repo)"):
        """
        Initialize the SPARQL executor.
        
        Args:
            endpoint: The SPARQL endpoint URL
            user_agent: User agent string for requests
        """
        self.endpoint = endpoint
        self.headers = {
            'User-Agent': user_agent,
            'Accept': 'application/sparql-results+json'
        }
    
    def execute_query(self, query: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute a SPARQL query against Wikidata.
        
        Args:
            query: The SPARQL query string
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary containing the query results
            
        Raises:
            Exception: If the query fails
        """
        try:
            # Add rate limiting to be respectful to the service
            time.sleep(0.1)
            
            # Make the request
            response = requests.get(
                self.endpoint,
                params={'query': query},
                headers=self.headers,
                timeout=timeout
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            result = response.json()
            
            # Transform to a more convenient format
            if 'results' in result and 'bindings' in result['results']:
                bindings = result['results']['bindings']
                
                # Extract simplified results
                simplified_results = []
                for binding in bindings:
                    row = {}
                    for var, value in binding.items():
                        if value['type'] == 'uri':
                            # Extract QID from URI if it's a Wikidata entity
                            uri = value['value']
                            if 'wikidata.org/entity/' in uri:
                                row[var] = uri.split('/')[-1]  # Extract QID
                                row[var + '_uri'] = uri  # Keep full URI
                            else:
                                row[var] = uri
                        else:
                            row[var] = value['value']
                    simplified_results.append(row)
                
                return {
                    'success': True,
                    'results': simplified_results,
                    'count': len(simplified_results),
                    'raw_results': result
                }
            else:
                return {
                    'success': True,
                    'results': [],
                    'count': 0,
                    'raw_results': result
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Query timeout',
                'results': []
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'results': []
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Invalid JSON response: {str(e)}',
                'results': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'results': []
            }

def create_sparql_executor() -> WikidataSPARQLExecutor:
    """
    Factory function to create a SPARQL executor.
    
    Returns:
        WikidataSPARQLExecutor instance
    """
    return WikidataSPARQLExecutor()

# Example usage and testing
if __name__ == "__main__":
    executor = create_sparql_executor()
    
    # Test query: Get the last 3 popes
    test_query = """
    SELECT ?pope ?popeLabel ?startDate WHERE {
      ?pope wdt:P39 wd:Q9951 .  # Position held: Pope
      ?pope p:P39 ?statement .
      ?statement ps:P39 wd:Q9951 .
      OPTIONAL { ?statement pq:P580 ?startDate . }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
    }
    ORDER BY DESC(?startDate)
    LIMIT 3
    """
    
    print("Testing SPARQL executor...")
    result = executor.execute_query(test_query)
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Found {result['count']} results:")
        for i, pope in enumerate(result['results'], 1):
            print(f"{i}. {pope.get('popeLabel', 'Unknown')} ({pope.get('pope', 'Unknown')}) - Started: {pope.get('startDate', 'Unknown')}")
    else:
        print(f"Error: {result['error']}")
