# Wikidata MCP Server (SSE Version)

A Model Context Protocol (MCP) server with SSE transport that connects Large Language Models to Wikidata's structured knowledge base. This server enables LLMs to search for entities, retrieve metadata, query relationships, and execute SPARQL queries to access factual information from Wikidata.

## Features

- Search for Wikidata entities by name
- Search for Wikidata properties by name
- Retrieve entity metadata (labels, descriptions)
- Execute SPARQL queries against Wikidata's endpoint
- Access common property references and SPARQL examples
- Use prompt templates for common Wikidata interaction patterns
- **SSE Transport**: Network-accessible MCP server (vs. stdio in the original version)

## Installation

### Prerequisites

- Python 3.10+
- Virtual environment tool (venv, conda, etc.)

### Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Server

To run the server locally:

```bash
python server_sse.py
```

This will start the server on `0.0.0.0:8000`.

### Connecting to the Server

You can connect to the server using any MCP client that supports SSE transport. The server URL will be:

```
http://localhost:8000
```

### Available Tools

The server provides the following tools:

1. `search_wikidata_entity`: Search for a Wikidata entity by name
2. `search_wikidata_property`: Search for a Wikidata property by name
3. `get_wikidata_metadata`: Get metadata for a Wikidata entity
4. `get_wikidata_properties`: Get all properties for a Wikidata entity
5. `execute_wikidata_sparql`: Execute a SPARQL query on Wikidata
6. `find_entity_facts`: Search for an entity and find its facts
7. `get_related_entities`: Find entities related to a given entity

### Available Resources

The server provides the following resources:

1. `wikidata://common-properties`: A list of commonly used Wikidata properties
2. `wikidata://sparql-examples`: Example SPARQL queries for common Wikidata tasks

## Deployment on Vercel

This SSE version can be deployed on Vercel. Create a `vercel.json` file with the following content:

```json
{
  "builds": [
    {
      "src": "server_sse.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "server_sse.py"
    }
  ]
}
```

Then deploy using the Vercel CLI:

```bash
vercel
```

## Integration with NANDA

This SSE version of the Wikidata MCP server can be integrated with the NANDA (Networked Agents And Decentralized AI) ecosystem:

1. Deploy the server to a publicly accessible URL
2. Register the server in the [NANDA Registry](https://ui.nanda-registry.com)
3. Other agents in the NANDA ecosystem can then discover and use your Wikidata knowledge server

## Differences from stdio Version

The main difference between this version and the original stdio version is the transport mechanism:

- **stdio version**: Runs locally and communicates through standard input/output streams. Ideal for local integrations like Claude Desktop.
- **SSE version**: Runs as a web server and communicates through HTTP with Server-Sent Events. Ideal for network access and integration with the NANDA ecosystem.

The core functionality (tools, resources, prompts) remains the same between both versions.

## License

MIT
