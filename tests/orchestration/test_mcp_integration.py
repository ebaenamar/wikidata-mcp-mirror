import unittest
import json
import datetime
from unittest.mock import patch
from orchestration.mcp_integration import process_natural_language_query

class TestMCPIntegration(unittest.TestCase):
    @patch('orchestration.query_orchestrator.QueryOrchestrator.process_query')
    def test_process_natural_language_query(self, mock_process_query):
        # Configure the mock to return a simulated result
        mock_result = {
            "results": {
                "bindings": [
                    {"itemLabel": {"value": "Francis"}},
                    {"itemLabel": {"value": "Benedict XVI"}},
                    {"itemLabel": {"value": "John Paul II"}}
                ]
            }
        }
        mock_process_query.return_value = mock_result
        
        # Process a query
        result_json = process_natural_language_query("last 3 popes")
        result = json.loads(result_json)
        
        # Verify that the orchestrator was called with default date (today)
        mock_process_query.assert_called_once()
        args, _ = mock_process_query.call_args
        self.assertEqual(args[0], "last 3 popes")
        
        # Verify that the result is as expected
        self.assertEqual(result, mock_result)
        
    @patch('orchestration.query_orchestrator.QueryOrchestrator.process_query')
    def test_process_query_with_custom_date(self, mock_process_query):
        # Configure the mock to return a simulated result with metadata
        test_date = datetime.date(2023, 1, 1)
        mock_result = {
            "results": {
                "bindings": [{"itemLabel": {"value": "Francis"}}]
            },
            "metadata": {
                "current_date": test_date.isoformat(),
                "query_processed_on": datetime.datetime.now().isoformat()
            }
        }
        mock_process_query.return_value = mock_result
        
        # Process a query with a specific date
        result_json = process_natural_language_query("current pope", test_date)
        result = json.loads(result_json)
        
        # Verify that the orchestrator was called with the custom date
        mock_process_query.assert_called_once()
        args, _ = mock_process_query.call_args
        self.assertEqual(args[0], "current pope")
        self.assertEqual(args[1], test_date)
        
        # Verify that the result contains the metadata with the custom date
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["current_date"], test_date.isoformat())
    
    @patch('orchestration.query_orchestrator.QueryOrchestrator.process_query')
    def test_process_query_with_error(self, mock_process_query):
        # Configure the mock to throw an exception
        mock_process_query.side_effect = Exception("Test error")
        
        # Process a query that will generate an error
        result_json = process_natural_language_query("query with error")
        result = json.loads(result_json)
        
        # Verify that the error was handled correctly
        self.assertIn("error", result)
        
        # Verify that error responses include current date metadata
        self.assertIn("metadata", result)
        self.assertIn("current_date", result["metadata"])
        self.assertIn("query_processed_on", result["metadata"])
        
    @patch('orchestration.query_orchestrator.QueryOrchestrator.process_query')
    def test_process_query_with_error_and_custom_date(self, mock_process_query):
        # Configure the mock to throw an exception
        mock_process_query.side_effect = Exception("Test error")
        
        # Use a specific test date
        test_date = datetime.date(2023, 1, 1)
        
        # Process a query that will generate an error with a custom date
        result_json = process_natural_language_query("query with error", test_date)
        result = json.loads(result_json)
        
        # Verify that the error was handled correctly
        self.assertIn("error", result)
        
        # Verify that error responses include the custom date metadata
        self.assertIn("metadata", result)
        self.assertEqual(result["metadata"]["current_date"], test_date.isoformat())

if __name__ == "__main__":
    unittest.main()
