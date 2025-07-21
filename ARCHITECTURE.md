# Wikidata MCP Architecture

## Overview

This document describes the optimized architecture for the Wikidata MCP (Model Context Protocol) system, designed to balance **speed**, **accuracy**, and **verifiability**.

## Architecture Design Principles

Based on empirical benchmarking, we implement a **hybrid architecture** that uses:

1. **Fast basic tools** for simple queries (140-250ms)
2. **Advanced orchestration** only for complex queries requiring temporal/relational analysis (1-11s)

## MCP Tools

### 🚀 Basic Tools (Fast & Reliable)

#### 1. `search_wikidata_entity`
- **Performance**: 140-250ms
- **Use for**: Simple entity lookups, getting QIDs
- **Example**: "Albert Einstein" → Q937

#### 2. `search_wikidata_property`  
- **Performance**: ~200ms
- **Use for**: Finding property IDs
- **Example**: "birth date" → P569

#### 3. `get_wikidata_metadata`
- **Performance**: ~200ms
- **Use for**: Entity labels, descriptions, aliases
- **Example**: Q937 → Einstein's metadata

#### 4. `get_wikidata_properties`
- **Performance**: ~200ms
- **Use for**: All properties of an entity
- **Example**: Q937 → Einstein's properties

#### 5. `execute_wikidata_sparql`
- **Performance**: ~200ms
- **Use for**: Direct SPARQL queries
- **Example**: Custom SPARQL for specific data

### 🧠 Advanced Tool (Complex Queries)

#### 6. `query_wikidata_complex`
- **Performance**: 1-11s (50x slower for simple queries)
- **Use for**: Temporal queries, complex relationships
- **Examples**:
  - ✅ "last 3 popes" (1.3s)
  - ✅ "recent presidents of France" (1.5s)
  - ✅ "who was pope in 1978" (7.8s)
  - ❌ "Albert Einstein" (11s vs 250ms with basic tool)

## Performance Benchmarks

### Simple Entity Queries
```
Query: "Albert Einstein"
- Basic tool:    250ms → Q937
- Advanced tool: 11,345ms → Success
- Speed difference: 45x slower

Query: "Paris"  
- Basic tool:    166ms → Q90
- Advanced tool: 9,007ms → Success
- Speed difference: 54x slower
```

### Temporal Queries (Advanced Only)
```
Query: "last 3 popes"
- Advanced tool: 1,330ms → Success

Query: "recent presidents of France"
- Advanced tool: 1,497ms → Success

Query: "who was pope in 1978"
- Advanced tool: 7,823ms → Success
```

## Usage Guidelines

### ✅ When to Use Basic Tools
- Simple entity searches
- Property lookups
- Metadata retrieval
- Direct SPARQL queries
- Any query that can be answered with known entities/properties

### ✅ When to Use Advanced Tool
- Temporal queries ("last 3...", "recent...", "who was X in year Y")
- Complex relationships requiring multiple entities
- Queries needing natural language understanding
- Multi-step reasoning

### ❌ Anti-patterns
- Using advanced tool for simple entity searches
- Using basic tools for temporal queries
- Mixing tools unnecessarily

## System Components

### Core Components
- **`wikidata_api.py`**: Basic Wikidata API functions
- **`server_sse.py`**: MCP server with optimized tools
- **`orchestration/`**: Advanced query processing system

### Orchestration System
- **`query_orchestrator.py`**: Main orchestration logic
- **`temporal_specialist.py`**: Temporal query handling
- **`mcp_integration.py`**: Integration with MCP server
- **`vector_db_client.py`**: Vector database for entity retrieval

## Environment Variables

```bash
# Required for advanced tool
WIKIDATA_VECTORDB_API_KEY=your_api_key_here

# Optional server configuration
PORT=8000
WORKERS=1
TIMEOUT=30
KEEPALIVE=2
```

## Deployment

The system is containerized and ready for deployment:

```bash
# Local development
pip install -e .
python -m wikidata_mcp

# Docker
docker build -t wikidata-mcp .
docker run -p 8000:8000 -e WIKIDATA_VECTORDB_API_KEY=your_key wikidata-mcp
```

## Testing

Run the benchmark to verify performance:

```bash
# Fair benchmark comparing same queries
python fair_benchmark.py

# Original benchmark for design documentation
python benchmark_tools.py
```

## Design Decisions

### Why Hybrid Architecture?
1. **Speed**: Basic tools are 50x faster for simple queries
2. **Accuracy**: Advanced tool handles complex queries basic tools cannot
3. **Verifiability**: Clear separation of concerns, easy to debug
4. **Maintainability**: Simple tools are reliable, complex logic isolated

### Removed Components
- **Redundant tools**: `find_entity_facts`, `get_related_entities`
- **Wrapper functions**: `enhanced_execute_wikidata_sparql`
- **Unused imports**: Cleaned up for performance

### Future Enhancements
- Automatic tool selection based on query analysis
- Caching for frequently accessed entities
- Query optimization for common patterns
- Fallback mechanisms for advanced tool failures

## Conclusion

This architecture provides an optimal balance of speed, accuracy, and maintainability by using the right tool for each type of query. The 50x performance difference for simple queries makes the hybrid approach essential for production use.
