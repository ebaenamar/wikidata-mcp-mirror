"""
FastAPI application for the Wikidata MCP Server.
"""
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="Wikidata MCP Server",
    description="A Model Context Protocol server for querying Wikidata",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", response_class=JSONResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": app.version,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Query endpoint for testing orchestration
@app.post("/query")
async def query_wikidata(request: dict):
    """Query endpoint for testing the orchestration system."""
    try:
        from .orchestration.mcp_integration import process_natural_language_query
        query = request.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        result = process_natural_language_query(query)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Main endpoint for MCP communication
@app.get("/messages/")
async def get_messages():
    """SSE endpoint for MCP communication."""
    # This is a placeholder - implement actual SSE logic here
    return {"message": "SSE endpoint"}

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic information."""
    return """
    <html>
        <head>
            <title>Wikidata MCP Server</title>
        </head>
        <body>
            <h1>Wikidata MCP Server</h1>
            <p>Welcome to the Wikidata Model Context Protocol server.</p>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/messages/">SSE Endpoint</a></li>
            </ul>
        </body>
    </html>
    """

# Error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Main entry point for running the server directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("wikidata_mcp.api:app", host="0.0.0.0", port=port, reload=True)
