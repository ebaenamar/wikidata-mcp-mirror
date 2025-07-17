# Wikidata MCP Server with Vector DB Integration

A Model Context Protocol (MCP) server with Server-Sent Events (SSE) transport that connects Large Language Models to Wikidata's structured knowledge base, enhanced with Vector Database capabilities for improved semantic search. This server enables LLMs to search for entities, retrieve metadata, query relationships, and execute SPARQL queries to access factual information from Wikidata with enhanced accuracy through vector embeddings.

## Features

- **SSE Transport**: Network-accessible MCP server
- **Vector DB Integration**: Enhanced semantic search using vector embeddings
- **Intelligent Caching**: Configurable caching system for improved performance
- **Query Feedback**: Learning system that improves over time based on user interactions
- Search for Wikidata entities by name with semantic understanding
- Search for Wikidata properties by name
- Retrieve entity metadata (labels, descriptions)
- Get entity properties and their values
- Execute SPARQL queries against Wikidata's endpoint
- Find entity facts with optional property filtering
- Get related entities with optional relation filtering
- Access common property references and SPARQL examples
- Use prompt templates for common Wikidata interaction patterns

## Live Demo

The server is deployed and accessible at:

- **URL**: [https://wikidata-mcp-mirror.onrender.com](https://wikidata-mcp-mirror.onrender.com)
- **SSE Endpoint**: [https://wikidata-mcp-mirror.onrender.com/messages/](https://wikidata-mcp-mirror.onrender.com/messages/)
- **Health Check**: [https://wikidata-mcp-mirror.onrender.com/health](https://wikidata-mcp-mirror.onrender.com/health)

## Usage with Claude Desktop

To use this server with Claude Desktop:

1. Edit the Claude Desktop configuration file located at:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. Configure it to use the remote MCP server:
   ```json
   {
     "mcpServers": {
       "Wikidata Knowledge Remote": {
         "command": "mcp-remote",
         "args": [
           "https://wikidata-mcp-mirror.onrender.com/messages/"
         ]
       }
     }
   }
   ```

3. Restart Claude Desktop

4. When using Claude, you can now access Wikidata knowledge through the configured MCP server.

## Deployment

### Deploying to Render

1. **Create a new Web Service** in your Render dashboard
2. **Connect your GitHub repository**
3. **Configure the service**:
   - **Build Command**: `pip install -e .`
   - **Start Command**: `python -m wikidata_mcp.api`
4. **Set Environment Variables**:
   - Add all variables from `.env.example`
   - For production, set `DEBUG=false`
   - Make sure to set a proper `WIKIDATA_VECTORDB_API_KEY`
5. **Deploy**

The service will be available at `https://your-service-name.onrender.com`

## Environment Setup

### Prerequisites

- Python 3.10+
- Virtual environment tool (venv, conda, etc.)
- Vector DB API key (for enhanced semantic search)

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Required for Vector DB integration

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/wikidata-mcp-mirror.git
   cd wikidata-mcp-mirror
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -e .
   ```

4. Create a `.env` file based on `.env.example` and configure your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the application:
   ```bash
   # Development
   python -m wikidata_mcp.api
   
   # Production (with Gunicorn)
   gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --keep-alive 5 --worker-class uvicorn.workers.UvicornWorker wikidata_mcp.api:app
   ```

   The server will start on `http://localhost:8000` by default with the following endpoints:
   - `GET /health` - Health check
   - `GET /messages/` - SSE endpoint for MCP communication
   - `GET /docs` - Interactive API documentation (if enabled)
   - `GET /metrics` - Prometheus metrics (if enabled)

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8000 | Port to run the server on |
| `WORKERS` | 4 | Number of worker processes |
| `TIMEOUT` | 120 | Worker timeout in seconds |
| `KEEPALIVE` | 5 | Keep-alive timeout in seconds |
| `DEBUG` | false | Enable debug mode |
| `LOG_LEVEL` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `USE_VECTOR_DB` | true | Enable/disable vector DB integration |
| `USE_CACHE` | true | Enable/disable caching system |
| `USE_FEEDBACK` | true | Enable/disable feedback system |
| `CACHE_TTL_SECONDS` | 3600 | Cache time-to-live in seconds |
| `CACHE_MAX_SIZE` | 1000 | Maximum number of items in cache |
| `WIKIDATA_VECTORDB_API_KEY` | | API key for the vector DB service |

### Running with Docker

1. Build the Docker image:
   ```bash
   docker build -t wikidata-mcp .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env-file .env wikidata-mcp
   ```

### Running with Docker Compose

1. Start the application:
   ```bash
   docker-compose up --build
   ```

2. For production, use the production compose file:
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

## Monitoring

The service exposes Prometheus metrics at `/metrics` when the `PROMETHEUS_METRICS` environment variable is set to `true`.

### Health Check

```bash
curl http://localhost:8000/health
```

### Metrics

```bash
curl http://localhost:8000/metrics
```

## Testing

### Running Tests

Run the test suite with:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/orchestration/test_query_orchestrator.py -v

# Run with coverage report
pytest --cov=wikidata_mcp tests/
```

### Integration Tests

To test the Vector DB integration, you'll need to set the `WIKIDATA_VECTORDB_API_KEY` environment variable:

```bash
WIKIDATA_VECTORDB_API_KEY=your_key_here pytest tests/orchestration/test_vectordb_integration.py -v
```

### Test Client

You can also test the server using the included test client:

```bash
python test_mcp_client.py
```

Or manually with curl:

```bash
# Connect to SSE endpoint
curl -N -H "Accept: text/event-stream" https://wikidata-mcp-mirror.onrender.com/messages/

# Send a message (replace SESSION_ID with the one received from the SSE endpoint)
curl -X POST "https://wikidata-mcp-mirror.onrender.com/messages/?session_id=YOUR_SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"0.1.0"}},"id":0}'
```

## Deployment on Render.com

This server is configured for deployment on Render.com using the `render.yaml` file.

### Deployment Configuration

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker server_sse:app`
- **Environment Variables**:
  - `PORT`: 10000
- **Health Check Path**: `/health`

### Docker Support

The repository includes a Dockerfile that's used by Render.com for containerized deployment. This allows the server to run in a consistent environment with all dependencies properly installed.

### How to Deploy

1. Fork or clone this repository to your GitHub account
2. Create a new Web Service on Render.com
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file and configure the deployment
5. Click "Create Web Service"

After deployment, you can access your server at the URL provided by Render.com.

## Architecture

The server is built using:

- **FastAPI**: For handling HTTP requests and routing
- **SSE Transport**: For bidirectional communication with clients
- **MCP Framework**: For implementing the Model Context Protocol
- **Wikidata API**: For accessing Wikidata's knowledge base

### Key Components

- `server_sse.py`: Main server implementation with SSE transport
- `wikidata_api.py`: Functions for interacting with Wikidata's API and SPARQL endpoint
- `requirements.txt`: Dependencies for the project
- `Dockerfile`: Container configuration for Docker deployment on Render
- `render.yaml`: Configuration for deployment on Render.com
- `test_mcp_client.py`: Test client for verifying server functionality

## Available MCP Tools

The server provides the following MCP tools:

- `search_wikidata_entity`: Search for entities by name
- `search_wikidata_property`: Search for properties by name
- `get_wikidata_metadata`: Get entity metadata (label, description)
- `get_wikidata_properties`: Get all properties for an entity
- `execute_wikidata_sparql`: Execute a SPARQL query
- `find_entity_facts`: Search for an entity and find its facts
- `get_related_entities`: Find entities related to a given entity

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the Model Context Protocol (MCP) specification
- Uses Wikidata as the knowledge source
- Inspired by the MCP examples from the official documentation
