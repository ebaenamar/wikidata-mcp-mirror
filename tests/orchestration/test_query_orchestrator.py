import unittest
import json
from orchestration.query_orchestrator import QueryOrchestrator

class TestQueryOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = QueryOrchestrator()
    
    def test_process_generic_query(self):
        # Process a generic query
        result = self.orchestrator.process_query("information about cats")
        
        # Verify it was handled as a generic query
        self.assertIn("warning", result)
        self.assertEqual(result["query_type"], "generic_query")
        
    def test_analyze_temporal_query(self):
        # Verify that the analyzer correctly detects a temporal query
        signal = self.orchestrator.analyzer.analyze("last 3 popes")
        self.assertEqual(signal.query_type, "temporal_query")
        self.assertEqual(signal.limit_constraints, 3)
        self.assertIn("Q9951", signal.entities)  # ID of "pope" in Wikidata

if __name__ == "__main__":
    unittest.main()
