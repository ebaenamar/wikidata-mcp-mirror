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

## Deployment on Render

To deploy this MCP server with SSE transport on Render, follow these steps:

1. Create a Render account if you don't have one.

2. From the Render dashboard, click "New" and select "Web Service".

3. Connect your GitHub repository (https://github.com/ebaenamar/wikidata-mcp) or upload the code directly.

4. Configure the service with the following parameters:
   - **Name**: wikidata-mcp-server (or the name you prefer)
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker server_sse:app`

5. Click "Create Web Service" and wait for the deployment to complete.

6. Once deployed, Render will provide a URL (e.g., `https://wikidata-mcp-server.onrender.com`).

7. To use this server with Claude or any other MCP client, configure the server URL as:
   ```
   https://your-app.onrender.com/sse
   ```

## Integration with NANDA

To register this server in the NANDA ecosystem, you can use the `nanda_register.py` script included:

```bash
python nanda_register.py --url https://your-app.onrender.com/sse --name "Wikidata Knowledge Server"
```

## Integration with Claude Desktop

To configure Claude Desktop to use this remote MCP server:

1. Edit the Claude Desktop configuration file:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. Update the configuration to use the remote server:
   ```json
   {
     "mcpCommand": "npx",
     "mcpArgs": ["mcp-remote", "https://your-app.onrender.com/sse"]
   }
   ```

3. Restart Claude Desktop to apply the changes.

## Testing

Once configured, you can test the server with Claude using prompts like:

- "¿Quién es Marie Curie según Wikidata?"
- "¿Cuáles son las propiedades principales de la Luna en Wikidata?"
- "Ejecuta una consulta SPARQL para encontrar los 5 ríos más largos del mundo."

## Differences from stdio Version

The main difference between this version and the original stdio version is the transport mechanism:

- **stdio version**: Runs locally and communicates through standard input/output streams. Ideal for local integrations like Claude Desktop.
- **SSE version**: Runs as a web server and communicates through HTTP with Server-Sent Events. Ideal for network access and integration with the NANDA ecosystem.

The core functionality (tools, resources, prompts) remains the same between both versions.

## License

MIT
