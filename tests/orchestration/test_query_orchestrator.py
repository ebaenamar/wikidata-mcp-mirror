import unittest
import json
import datetime
from unittest.mock import patch
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
        
        # Verify metadata with current date is included
        self.assertIn("metadata", result)
        self.assertIn("current_date", result["metadata"])
        self.assertIn("query_processed_on", result["metadata"])
        
    def test_analyze_temporal_query(self):
        # Verify that the analyzer correctly detects a temporal query
        signal = self.orchestrator.analyzer.analyze("last 3 popes")
        self.assertEqual(signal.query_type, "temporal_query")
        self.assertEqual(signal.limit_constraints, 3)
        self.assertIn("Q9951", signal.entities)  # ID of "pope" in Wikidata
        
        # Verify current date is set
        self.assertIsInstance(signal.current_date, datetime.date)
        
    def test_process_query_with_custom_date(self):
        # Test with a specific date
        test_date = datetime.date(2023, 1, 1)
        result = self.orchestrator.process_query("information about cats", test_date)
        
        # Verify the custom date was used
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["current_date"], test_date.isoformat())
        
    def test_process_temporal_query_with_current_filter(self):
        # Test a query that should use the current date filter
        with patch('orchestration.temporal_specialist.TemporalSpecialist.execute_sparql') as mock_execute:
            # Mock the SPARQL execution to return a valid result
            mock_execute.return_value = json.dumps({
                "results": {
                    "bindings": [{
                        "item": {"value": "http://www.wikidata.org/entity/Q450207"},
                        "itemLabel": {"value": "Francis"},
                        "startDate": {"value": "2013-03-13"}
                    }]
                }
            })
            
            # Process a query about the current pope
            result = self.orchestrator.process_query("current pope")
            
            # Verify metadata with current date is included
            self.assertIn("metadata", result)
            self.assertIn("current_date", result["metadata"])
            
            # Verify the SPARQL query was called with the right template
            mock_execute.assert_called_once()
            # The call should include FILTER NOT EXISTS for the end date
            call_args = mock_execute.call_args[0][0]
            self.assertIn("FILTER NOT EXISTS", call_args)

if __name__ == "__main__":
    unittest.main()
