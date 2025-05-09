#!/bin/bash

# Test script for Wikidata MCP Server

echo "=== Testing Wikidata MCP Server ==="
echo "Server URL: https://wikidata-mcp-mirror.onrender.com"

# Step 1: Check if the server is running
echo "\n=== Step 1: Checking server health ==="
curl -s https://wikidata-mcp-mirror.onrender.com/health

# Step 2: Connect to SSE endpoint to get a session ID
echo "\n\n=== Step 2: Connecting to SSE endpoint ==="
echo "(Starting connection, will capture session ID)"

# Use a temporary file to store the SSE response
TMP_FILE=$(mktemp)

# Start curl in the background to capture the SSE stream
curl -N -H "Accept: text/event-stream" https://wikidata-mcp-mirror.onrender.com/sse > "$TMP_FILE" &
CURL_PID=$!

# Wait a moment for the connection to establish
sleep 3

# Extract the session ID from the response
SESSION_ID=$(grep -o 'session_id=[a-zA-Z0-9]*' "$TMP_FILE" | head -1 | cut -d= -f2)

# Kill the background curl process
kill $CURL_PID 2>/dev/null

if [ -z "$SESSION_ID" ]; then
  echo "Failed to get session ID. Check the raw response:"
  cat "$TMP_FILE"
  rm "$TMP_FILE"
  exit 1
fi

echo "Got session ID: $SESSION_ID"
rm "$TMP_FILE"

# Step 3: Test SPARQL query
echo "\n=== Step 3: Testing SPARQL query ==="
SPARQL_QUERY='SELECT ?item ?itemLabel ?birth ?death ?successor ?successorLabel WHERE { ?item wdt:P39 wd:Q19546. ?item rdfs:label "Pope Francis"@en. OPTIONAL { ?item wdt:P569 ?birth. } OPTIONAL { ?item wdt:P570 ?death. } OPTIONAL { ?item wdt:P1366 ?successor. } SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }'

echo "Sending SPARQL query for Pope Francis..."
curl -s -X POST "https://wikidata-mcp-mirror.onrender.com/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d "{\
    \"jsonrpc\": \"2.0\",\
    \"method\": \"execute\",\
    \"params\": {\
      \"toolName\": \"execute_wikidata_sparql\",\
      \"toolInput\": {\
        \"sparql_query\": \"$SPARQL_QUERY\"\
      }\
    },\
    \"id\": 1\
  }"

# Step 4: Test find_entity_facts
echo "\n\n=== Step 4: Testing find_entity_facts ==="
echo "Sending entity facts query for Pope Francis..."
curl -s -X POST "https://wikidata-mcp-mirror.onrender.com/messages?session_id=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d "{\
    \"jsonrpc\": \"2.0\",\
    \"method\": \"execute\",\
    \"params\": {\
      \"toolName\": \"find_entity_facts\",\
      \"toolInput\": {\
        \"entity_name\": \"Pope Francis\"\
      }\
    },\
    \"id\": 2\
  }"

echo "\n\n=== Tests completed ==="
