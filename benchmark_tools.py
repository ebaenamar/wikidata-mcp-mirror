#!/usr/bin/env python3
"""
Benchmark script to measure performance of different MCP tools
"""
import time
import json
import statistics
from typing import List, Dict, Any
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wikidata_api import search_entity, get_entity_metadata, execute_sparql
from wikidata_mcp.orchestration.mcp_integration import process_natural_language_query

def benchmark_tool(tool_func, queries: List[str], tool_name: str) -> Dict[str, Any]:
    """Benchmark a tool with multiple queries"""
    results = {
        'tool_name': tool_name,
        'queries_tested': len(queries),
        'latencies': [],
        'success_count': 0,
        'error_count': 0,
        'errors': []
    }
    
    for query in queries:
        start_time = time.time()
        try:
            result = tool_func(query)
            latency = time.time() - start_time
            results['latencies'].append(latency)
            
            # Check if result indicates success
            if isinstance(result, str) and ('error' in result.lower() or 'no entity found' in result.lower()):
                results['error_count'] += 1
                results['errors'].append(f"Query: {query} -> {result}")
            else:
                results['success_count'] += 1
                
        except Exception as e:
            latency = time.time() - start_time
            results['latencies'].append(latency)
            results['error_count'] += 1
            results['errors'].append(f"Query: {query} -> Exception: {str(e)}")
    
    # Calculate statistics
    if results['latencies']:
        results['avg_latency'] = statistics.mean(results['latencies'])
        results['median_latency'] = statistics.median(results['latencies'])
        results['min_latency'] = min(results['latencies'])
        results['max_latency'] = max(results['latencies'])
    
    results['success_rate'] = results['success_count'] / len(queries) * 100
    
    return results

def main():
    # Test queries for different scenarios
    simple_entity_queries = [
        "Albert Einstein",
        "Paris",
        "Python programming language",
        "Barack Obama",
        "COVID-19"
    ]
    
    temporal_queries = [
        "last 3 popes",
        "recent presidents of France",
        "current prime minister of UK",
        "who was pope in 1978",
        "presidents of USA in 20th century"
    ]
    
    complex_queries = [
        "Nobel Prize winners in Physics from Germany",
        "cities with population over 1 million in Europe",
        "movies directed by Christopher Nolan",
        "books written by Gabriel García Márquez",
        "universities founded before 1500"
    ]
    
    print("🚀 Starting MCP Tools Benchmark")
    print("=" * 50)
    
    # Benchmark 1: Simple entity search
    print("\n📊 Benchmarking: search_entity")
    entity_results = benchmark_tool(search_entity, simple_entity_queries, "search_entity")
    
    # Benchmark 2: Advanced queries (if available)
    print("\n📊 Benchmarking: advanced_query")
    try:
        advanced_results = benchmark_tool(process_natural_language_query, temporal_queries, "advanced_query")
    except Exception as e:
        print(f"❌ Advanced query tool not available: {e}")
        advanced_results = None
    
    # Print results
    print("\n" + "=" * 50)
    print("📈 BENCHMARK RESULTS")
    print("=" * 50)
    
    def print_results(results: Dict[str, Any]):
        print(f"\n🔧 Tool: {results['tool_name']}")
        print(f"   Queries tested: {results['queries_tested']}")
        print(f"   Success rate: {results['success_rate']:.1f}%")
        print(f"   Average latency: {results['avg_latency']*1000:.0f}ms")
        print(f"   Median latency: {results['median_latency']*1000:.0f}ms")
        print(f"   Min latency: {results['min_latency']*1000:.0f}ms")
        print(f"   Max latency: {results['max_latency']*1000:.0f}ms")
        
        if results['errors']:
            print(f"   ❌ Errors ({results['error_count']}):")
            for error in results['errors'][:3]:  # Show first 3 errors
                print(f"      {error}")
            if len(results['errors']) > 3:
                print(f"      ... and {len(results['errors']) - 3} more")
    
    print_results(entity_results)
    
    if advanced_results:
        print_results(advanced_results)
        
        # Comparison
        print(f"\n⚡ PERFORMANCE COMPARISON")
        print(f"   Speed difference: {advanced_results['avg_latency']/entity_results['avg_latency']:.1f}x slower")
        print(f"   Accuracy difference: {advanced_results['success_rate'] - entity_results['success_rate']:.1f}%")
    
    print(f"\n💡 RECOMMENDATION")
    if advanced_results and entity_results['success_rate'] > 90:
        if advanced_results['avg_latency'] > entity_results['avg_latency'] * 3:
            print("   Use HYBRID approach: Basic tools for simple queries, advanced for complex ones")
        else:
            print("   Use ADVANCED tool: Performance difference is acceptable")
    else:
        print("   Use BASIC tools: More reliable and faster")

if __name__ == "__main__":
    main()
