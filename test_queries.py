#!/usr/bin/env python3
"""
Simple test script to verify MCP server functionality
"""
import requests
import json
import sys

# URL of the MCP server
SERVER_URL = "https://wikidata-mcp-mirror.onrender.com"

def test_sparql_query():
    """Test a SPARQL query that was previously failing"""
    print("\n=== Testing SPARQL Query ===\n")
    
    # Initialize a session with the server
    session_response = requests.get(f"{SERVER_URL}/sse", 
                                  headers={"Accept": "text/event-stream"}, 
                                  stream=True)
    
    if session_response.status_code != 200:
        print(f"Failed to connect to SSE endpoint: {session_response.status_code}")
        return False
    
    # Extract session ID from response headers or URL
    session_id = None
    for line in session_response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if 'session_id=' in decoded_line:
                session_id = decoded_line.split('session_id=')[1].split('"')[0]
                break
    
    if not session_id:
        print("Failed to get session ID")
        return False
    
    print(f"Got session ID: {session_id}")
    
    # Close the SSE connection (we don't need to keep it open for this test)
    session_response.close()
    
    # Test the SPARQL query
    sparql_query = """
    SELECT ?item ?itemLabel ?birth ?death ?successor ?successorLabel WHERE {
      ?item wdt:P39 wd:Q19546.
      ?item rdfs:label "Pope Francis"@en.
      OPTIONAL { ?item wdt:P569 ?birth. }
      OPTIONAL { ?item wdt:P570 ?death. }
      OPTIONAL { ?item wdt:P1366 ?successor. }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    """
    
    payload = {
        "jsonrpc": "2.0",
        "method": "execute",
        "params": {
            "toolName": "execute_wikidata_sparql",
            "toolInput": {"sparql_query": sparql_query}
        },
        "id": 1
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{SERVER_URL}/messages/?session_id={session_id}",
        headers=headers,
        data=json.dumps(payload)
    )
    
    print(f"SPARQL Query Response Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response.status_code == 202

def test_find_entity_facts():
    """Test the find_entity_facts function that was previously failing"""
    print("\n=== Testing Find Entity Facts ===\n")
    
    # Initialize a session with the server
    session_response = requests.get(f"{SERVER_URL}/sse", 
                                  headers={"Accept": "text/event-stream"}, 
                                  stream=True)
    
    if session_response.status_code != 200:
        print(f"Failed to connect to SSE endpoint: {session_response.status_code}")
        return False
    
    # Extract session ID from response headers or URL
    session_id = None
    for line in session_response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if 'session_id=' in decoded_line:
                session_id = decoded_line.split('session_id=')[1].split('"')[0]
                break
    
    if not session_id:
        print("Failed to get session ID")
        return False
    
    print(f"Got session ID: {session_id}")
    
    # Close the SSE connection (we don't need to keep it open for this test)
    session_response.close()
    
    # Test the find_entity_facts function
    payload = {
        "jsonrpc": "2.0",
        "method": "execute",
        "params": {
            "toolName": "find_entity_facts",
            "toolInput": {"entity_name": "Pope Francis"}
        },
        "id": 2
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{SERVER_URL}/messages/?session_id={session_id}",
        headers=headers,
        data=json.dumps(payload)
    )
    
    print(f"Find Entity Facts Response Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response.status_code == 202

if __name__ == "__main__":
    print(f"Testing MCP server at {SERVER_URL}")
    
    sparql_success = test_sparql_query()
    entity_success = test_find_entity_facts()
    
    if sparql_success and entity_success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
