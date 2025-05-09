"""
Wikidata API Module

This module provides functions for interacting with the Wikidata API and SPARQL endpoint.
"""
import json
import requests
import traceback
import sys

# Ensure SPARQLWrapper is properly imported
try:
    from SPARQLWrapper import SPARQLWrapper, JSON
    print("Successfully imported SPARQLWrapper")
except ImportError as e:
    print(f"Error importing SPARQLWrapper: {e}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path}")
    
    # Try alternative import methods
    try:
        import pip
        print("Attempting to install SPARQLWrapper via pip...")
        pip.main(['install', 'SPARQLWrapper'])
        from SPARQLWrapper import SPARQLWrapper, JSON
        print("Successfully installed and imported SPARQLWrapper")
    except Exception as e2:
        print(f"Failed to install SPARQLWrapper: {e2}")
        
        # Define fallback implementation to avoid runtime errors
        print("Using fallback implementation for SPARQLWrapper")
        class SPARQLWrapper:
            def __init__(self, endpoint):
                self.endpoint = endpoint
                print(f"Fallback SPARQLWrapper initialized with endpoint: {endpoint}")
            
            def addCustomHttpHeader(self, header, value):
                print(f"Adding header {header}: {value}")
                pass
                
            def setQuery(self, query):
                print(f"Setting query: {query[:100]}...")
                self.query = query
                
            def setReturnFormat(self, format_type):
                print(f"Setting return format: {format_type}")
                pass
                
            def query(self):
                print("Executing fallback query (will return empty results)")
                class Result:
                    def convert(self):
                        return {"results": {"bindings": []}}
                return Result()
        
        # Define JSON constant if not available
        JSON = "json"

# Constants
WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "Wikidata MCP Server/1.0 (https://github.com/ebaenamar/wikidata-mcp; ebaenamar@gmail.com)"

def search_entity(query: str) -> str:
    """
    Search for a Wikidata entity ID by its name.
    
    Args:
        query: The search term
        
    Returns:
        The Wikidata entity ID (e.g., Q937 for Albert Einstein) or an error message
    """
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": query,
        "type": "item"
    }
    
    headers = {
        "User-Agent": USER_AGENT
    }
    
    try:
        response = requests.get(WIKIDATA_API_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "search" in data and len(data["search"]) > 0:
            return data["search"][0]["id"]
        else:
            return "No entity found"
    except requests.exceptions.RequestException as e:
        return f"Error searching for entity: {str(e)}"

def search_property(query: str) -> str:
    """
    Search for a Wikidata property ID by its name.
    
    Args:
        query: The search term
        
    Returns:
        The Wikidata property ID (e.g., P31 for "instance of") or an error message
    """
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": query,
        "type": "property"
    }
    
    headers = {
        "User-Agent": USER_AGENT
    }
    
    try:
        response = requests.get(WIKIDATA_API_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "search" in data and len(data["search"]) > 0:
            return data["search"][0]["id"]
        else:
            return "No property found"
    except requests.exceptions.RequestException as e:
        return f"Error searching for property: {str(e)}"

def get_entity_metadata(entity_id: str) -> dict:
    """
    Get label and description for a Wikidata entity.
    
    Args:
        entity_id: The Wikidata entity ID (e.g., Q937)
        
    Returns:
        A dictionary containing the entity's label and description
    """
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": entity_id,
        "languages": "en",
        "props": "labels|descriptions"
    }
    
    headers = {
        "User-Agent": USER_AGENT
    }
    
    try:
        response = requests.get(WIKIDATA_API_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "entities" in data and entity_id in data["entities"]:
            entity = data["entities"][entity_id]
            label = entity.get("labels", {}).get("en", {}).get("value", "No label found")
            description = entity.get("descriptions", {}).get("en", {}).get("value", "No description found")
            
            return {
                "id": entity_id,
                "label": label,
                "description": description
            }
        else:
            return {"error": f"Entity {entity_id} not found"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error retrieving entity metadata: {str(e)}"}

def get_entity_properties(entity_id: str) -> list:
    """
    Get all properties for a Wikidata entity.
    
    Args:
        entity_id: The Wikidata entity ID (e.g., Q937)
        
    Returns:
        A list of property-value pairs for the entity
    """
    sparql_query = f"""
    SELECT ?property ?propertyLabel ?value ?valueLabel
    WHERE {{
      wd:{entity_id} ?p ?statement.
      ?statement ?ps ?value.
      
      ?property wikibase:claim ?p.
      ?property wikibase:statementProperty ?ps.
      
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 50
    """
    
    return json.loads(execute_sparql(sparql_query))

def execute_sparql(sparql_query: str) -> str:
    """
    Execute a SPARQL query on Wikidata.
    
    Args:
        sparql_query: SPARQL query to execute
        
    Returns:
        JSON-formatted result of the query
    """
    print(f"Executing SPARQL query: {sparql_query[:100]}...")
    
    # Use direct requests to the SPARQL endpoint if SPARQLWrapper is not working
    if not hasattr(SPARQLWrapper, 'query') or getattr(SPARQLWrapper, 'query', None) is None:
        print("Using requests fallback for SPARQL query")
        return execute_sparql_with_requests(sparql_query)
    
    try:
        sparql = SPARQLWrapper(WIKIDATA_SPARQL_ENDPOINT)
        sparql.addCustomHttpHeader("User-Agent", USER_AGENT)
        
        # Add common prefixes to make queries easier to write
        prefixes = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX p: <http://www.wikidata.org/prop/>
        PREFIX ps: <http://www.wikidata.org/prop/statement/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>
        """
        
        # Add prefixes if they're not already in the query
        if not any(prefix in sparql_query for prefix in ["PREFIX", "prefix"]):
            full_query = prefixes + sparql_query
        else:
            full_query = sparql_query
        
        print(f"Setting query with SPARQLWrapper: {full_query[:100]}...")
        sparql.setQuery(full_query)
        sparql.setReturnFormat(JSON)
        
        print("Executing query with SPARQLWrapper...")
        results = sparql.query().convert()
        print("Query executed successfully")
        return json.dumps(results["results"]["bindings"])
    except Exception as e:
        print(f"Error with SPARQLWrapper: {e}")
        print("Falling back to requests method")
        return execute_sparql_with_requests(sparql_query)

def execute_sparql_with_requests(sparql_query: str) -> str:
    """
    Execute a SPARQL query using direct HTTP requests instead of SPARQLWrapper.
    
    Args:
        sparql_query: SPARQL query to execute
        
    Returns:
        JSON-formatted result of the query
    """
    try:
        # Add common prefixes to make queries easier to write
        prefixes = """
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX p: <http://www.wikidata.org/prop/>
        PREFIX ps: <http://www.wikidata.org/prop/statement/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>
        """
        
        # Add prefixes if they're not already in the query
        if not any(prefix in sparql_query for prefix in ["PREFIX", "prefix"]):
            full_query = prefixes + sparql_query
        else:
            full_query = sparql_query
            
        print(f"Executing SPARQL query with requests: {full_query[:100]}...")
        
        # Set up the request parameters
        params = {
            'query': full_query,
            'format': 'json'
        }
        
        headers = {
            'Accept': 'application/sparql-results+json',
            'User-Agent': USER_AGENT
        }
        
        # Make the request to the SPARQL endpoint
        response = requests.get(
            WIKIDATA_SPARQL_ENDPOINT,
            params=params,
            headers=headers
        )
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        results = response.json()
        print("Query executed successfully with requests")
        return json.dumps(results["results"]["bindings"])
    except Exception as e:
        error_details = {
            "error": f"Error executing query with requests: {str(e)}",
            "query": sparql_query,
            "error_type": str(type(e).__name__),
            "traceback": traceback.format_exc()
        }
        print(f"SPARQL Error Details:\n{json.dumps(error_details, indent=2)}")
        return json.dumps(error_details)
