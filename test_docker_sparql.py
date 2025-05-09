#!/usr/bin/env python3

"""
Test script to verify SPARQLWrapper functionality in Docker.
"""

import sys
import json

print("=== Testing SPARQLWrapper Import in Docker ===")
print(f"Python version: {sys.version}")

try:
    print("\nAttempting to import SPARQLWrapper...")
    from SPARQLWrapper import SPARQLWrapper, JSON
    print("SPARQLWrapper imported successfully!")
    
    # Test basic SPARQLWrapper functionality
    print("\nTesting basic SPARQLWrapper functionality...")
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    print("SPARQLWrapper instance created successfully!")
    
    # Set a simple query
    sparql.setQuery("""
    SELECT ?item ?itemLabel
    WHERE {
      ?item wdt:P31 wd:Q5.
      ?item wdt:P39 wd:Q11696.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    LIMIT 1
    """)
    print("Query set successfully!")
    
    # Set return format
    sparql.setReturnFormat(JSON)
    print("Return format set successfully!")
    
    # Execute query
    print("\nExecuting SPARQL query...")
    results = sparql.query().convert()
    print("Query executed successfully!")
    print(f"Results: {json.dumps(results['results']['bindings'], indent=2)}")
    
except ImportError as e:
    print(f"Error importing SPARQLWrapper: {e}")
    print("\nChecking installed packages:")
    import pkg_resources
    installed_packages = pkg_resources.working_set
    installed_packages_list = sorted([f"{i.key}=={i.version}" for i in installed_packages])
    for package in installed_packages_list:
        if "sparql" in package.lower():
            print(f"  {package}")
    
except Exception as e:
    print(f"Error during test: {e}")
    import traceback
    traceback.print_exc()
