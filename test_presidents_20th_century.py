#!/usr/bin/env python3

"""
Test script to query US presidents born in the 20th century using SPARQLWrapper.
"""

import json
from SPARQLWrapper import SPARQLWrapper, JSON

print("=== Querying US Presidents Born in the 20th Century ===")

# Initialize SPARQLWrapper
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

# Set the SPARQL query to find US presidents born in the 20th century
sparql_query = """
SELECT ?president ?presidentLabel ?birthDate ?birthYear ?deathDate ?deathYear
WHERE {
  ?president wdt:P39 wd:Q11696.  # Position held: President of the United States
  ?president wdt:P569 ?birthDate.  # Date of birth
  
  # Extract year from birthDate
  BIND(YEAR(?birthDate) AS ?birthYear)
  
  # Filter for presidents born in the 20th century (1900-1999)
  FILTER(?birthYear >= 1900 && ?birthYear < 2000)
  
  # Optional death date
  OPTIONAL { 
    ?president wdt:P570 ?deathDate.
    BIND(YEAR(?deathDate) AS ?deathYear)
  }
  
  # Get labels in English
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY ?birthYear
"""

# Set the query and return format
sparql.setQuery(sparql_query)
sparql.setReturnFormat(JSON)

try:
    # Execute the query
    print("Executing SPARQL query...")
    results = sparql.query().convert()
    
    # Process and display the results
    presidents = results["results"]["bindings"]
    print(f"\nFound {len(presidents)} US Presidents born in the 20th century:\n")
    
    for president in presidents:
        name = president.get("presidentLabel", {}).get("value", "Unknown")
        birth_date = president.get("birthDate", {}).get("value", "Unknown")
        birth_year = president.get("birthYear", {}).get("value", "Unknown")
        
        death_info = ""
        if "deathDate" in president:
            death_date = president.get("deathDate", {}).get("value", "Unknown")
            death_year = president.get("deathYear", {}).get("value", "Unknown")
            death_info = f", Died: {death_date} ({death_year})"
        
        print(f"• {name} - Born: {birth_date} ({birth_year}){death_info}")
    
    # Save the results to a JSON file
    with open("presidents_20th_century.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to presidents_20th_century.json")
    
except Exception as e:
    print(f"Error executing query: {e}")
    import traceback
    traceback.print_exc()
