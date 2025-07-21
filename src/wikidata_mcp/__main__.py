"""
Entry point for the wikidata_mcp package.
"""
import os
import uvicorn
from wikidata_mcp.api import app

def main():
    """Run the FastAPI application with uvicorn."""
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("wikidata_mcp.api:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    main()
