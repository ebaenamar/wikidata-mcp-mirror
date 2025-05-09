#!/usr/bin/env python3

"""
Simple test script to verify SPARQLWrapper functionality.
"""

import json
from SPARQLWrapper import SPARQLWrapper, JSON

# Test basic SPARQLWrapper functionality
print("Testing SPARQLWrapper with a simple query...")
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

# Execute query
print("Executing SPARQL query...")
results = sparql.query().convert()
print("Query executed successfully!")
print(f"Results: {json.dumps(results['results']['bindings'], indent=2)}")
