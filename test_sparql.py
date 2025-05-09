#!/usr/bin/env python3

"""
Test script to verify SPARQLWrapper functionality and fallback mechanism.
"""

import sys
import json
import traceback

print("=== Testing SPARQLWrapper Import and SPARQL Query Execution ===")
print(f"Python version: {sys.version}")

# Try to import SPARQLWrapper
try:
    print("\nAttempting to import SPARQLWrapper...")
    from SPARQLWrapper import SPARQLWrapper, JSON
    print("✅ SPARQLWrapper imported successfully!")
    
    # Test basic SPARQLWrapper functionality
    print("\nTesting basic SPARQLWrapper functionality...")
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery("""
    SELECT ?item ?itemLabel
    WHERE {
      ?item wdt:P31 wd:Q5.
      ?item wdt:P39 wd:Q11696.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    LIMIT 5
    """)
    sparql.setReturnFormat(JSON)
    print("✅ SPARQLWrapper query configured successfully!")
    
    # Execute query
    try:
        print("\nExecuting SPARQL query with SPARQLWrapper...")
        results = sparql.query().convert()
        print("✅ Query executed successfully!")
        print(f"Results: {json.dumps(results['results']['bindings'], indent=2)[:500]}...")
    except Exception as e:
        print(f"❌ Error executing query with SPARQLWrapper: {e}")
        traceback.print_exc()

except ImportError as e:
    print(f"❌ Error importing SPARQLWrapper: {e}")
    
    # Test fallback with requests
    print("\nTesting fallback with requests...")
    try:
        import requests
        print("✅ Requests module imported successfully!")
        
        # Set up the request parameters
        query = """
        SELECT ?item ?itemLabel
        WHERE {
          ?item wdt:P31 wd:Q5.
          ?item wdt:P39 wd:Q11696.
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
        }
        LIMIT 5
        """
        
        params = {
            'query': query,
            'format': 'json'
        }
        
        headers = {
            'Accept': 'application/sparql-results+json',
            'User-Agent': 'Wikidata MCP Test Script/1.0'
        }
        
        # Make the request to the SPARQL endpoint
        print("\nExecuting SPARQL query with requests...")
        response = requests.get(
            "https://query.wikidata.org/sparql",
            params=params,
            headers=headers
        )
        
        # Check if the request was successful
        response.raise_for_status()
        print("✅ Query executed successfully with requests!")
        
        # Parse the JSON response
        results = response.json()
        print(f"Results: {json.dumps(results['results']['bindings'], indent=2)[:500]}...")
    except Exception as e:
        print(f"❌ Error with requests fallback: {e}")
        traceback.print_exc()

# Now test our wikidata_api module
print("\n=== Testing our wikidata_api module ===")
try:
    print("Importing execute_sparql from wikidata_api...")
    from wikidata_api import execute_sparql
    print("✅ execute_sparql imported successfully!")
    
    # Test execute_sparql function
    print("\nTesting execute_sparql function...")
    query = """
    SELECT ?item ?itemLabel
    WHERE {
      ?item wdt:P31 wd:Q5.
      ?item wdt:P39 wd:Q11696.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    LIMIT 5
    """
    
    result = execute_sparql(query)
    print("✅ execute_sparql executed successfully!")
    print(f"Result: {result[:500]}...")
    
    # Parse the result to ensure it's valid JSON
    try:
        parsed_result = json.loads(result)
        print("✅ Result is valid JSON!")
    except json.JSONDecodeError as e:
        print(f"❌ Result is not valid JSON: {e}")
except Exception as e:
    print(f"❌ Error testing wikidata_api module: {e}")
    traceback.print_exc()

print("\n=== Test completed ===")
