import unittest
import os
from orchestration.query_analyzer import QueryAnalyzer

class TestQueryAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = QueryAnalyzer()
    
    def test_analyze_temporal_query(self):
        signal = self.analyzer.analyze("últimos 3 papas")
        self.assertEqual(signal.query_type, "temporal_query")
        self.assertEqual(signal.limit_constraints, 3)
        self.assertIn("Q9951", signal.entities)  # ID de "papa" en Wikidata
    
    def test_analyze_generic_query(self):
        signal = self.analyzer.analyze("información sobre gatos")
        self.assertEqual(signal.query_type, "generic_query")
        
    def test_analyze_without_number(self):
        signal = self.analyzer.analyze("últimos papas")
        self.assertEqual(signal.query_type, "temporal_query")
        self.assertIsNone(signal.limit_constraints)

if __name__ == "__main__":
    unittest.main()
