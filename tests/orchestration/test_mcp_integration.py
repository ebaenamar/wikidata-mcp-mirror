import unittest
import json
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
        
        # Verify that the orchestrator was called
        mock_process_query.assert_called_once_with("last 3 popes")
        
        # Verify that the result is as expected
        self.assertEqual(result, mock_result)
    
    @patch('orchestration.query_orchestrator.QueryOrchestrator.process_query')
    def test_process_query_with_error(self, mock_process_query):
        # Configure the mock to throw an exception
        mock_process_query.side_effect = Exception("Test error")
        
        # Process a query that will generate an error
        result_json = process_natural_language_query("query with error")
        result = json.loads(result_json)
        
        # Verify that the error was handled correctly
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()
