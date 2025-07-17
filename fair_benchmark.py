#!/usr/bin/env python3
"""
Fair benchmark comparing tools on the SAME queries
"""
import time
import json
import statistics
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wikidata_api import search_entity, get_entity_metadata, execute_sparql
from wikidata_mcp.orchestration.mcp_integration import process_natural_language_query

def time_function(func, query):
    """Time a single function call"""
    start = time.time()
    try:
        result = func(query)
        latency = time.time() - start
        success = True
        error = None
    except Exception as e:
        latency = time.time() - start
        result = None
        success = False
        error = str(e)
    
    return {
        'latency': latency,
        'success': success,
        'result': result,
        'error': error
    }

def main():
    print("🔬 FAIR BENCHMARK: Same queries, different tools")
    print("=" * 60)
    
    # Test the SAME queries on both tools
    test_queries = [
        "Albert Einstein",
        "Paris", 
        "Barack Obama"
    ]
    
    print("\n📊 Testing entity search queries on both tools:")
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Test basic tool
        basic_result = time_function(search_entity, query)
        print(f"   Basic tool:    {basic_result['latency']*1000:.0f}ms -> {basic_result['result']}")
        
        # Test advanced tool  
        advanced_result = time_function(process_natural_language_query, query)
        print(f"   Advanced tool: {advanced_result['latency']*1000:.0f}ms -> Success: {advanced_result['success']}")
        
        if basic_result['success'] and advanced_result['success']:
            speed_diff = advanced_result['latency'] / basic_result['latency']
            print(f"   Speed difference: {speed_diff:.1f}x slower")
    
    print("\n" + "=" * 60)
    print("🎯 TEMPORAL QUERIES (only advanced tool can handle these):")
    
    temporal_queries = [
        "last 3 popes",
        "recent presidents of France",
        "who was pope in 1978"
    ]
    
    for query in temporal_queries:
        print(f"\n🕐 Query: '{query}'")
        
        # Only advanced tool can handle these
        advanced_result = time_function(process_natural_language_query, query)
        print(f"   Advanced tool: {advanced_result['latency']*1000:.0f}ms -> Success: {advanced_result['success']}")
        
        if advanced_result['error']:
            print(f"   Error: {advanced_result['error']}")

if __name__ == "__main__":
    main()
