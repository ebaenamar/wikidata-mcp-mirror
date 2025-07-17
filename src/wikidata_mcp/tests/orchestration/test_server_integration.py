import unittest
import json
import datetime
from unittest.mock import patch, MagicMock
from orchestration.server_integration import is_sparql_query, enhanced_execute_wikidata_sparql

class TestServerIntegration(unittest.TestCase):
    def test_is_sparql_query(self):
        # Test with SPARQL queries
        self.assertTrue(is_sparql_query("SELECT * WHERE { ?s ?p ?o }"))
        self.assertTrue(is_sparql_query("ASK WHERE { ?s ?p ?o }"))
        self.assertTrue(is_sparql_query("CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }"))
        self.assertTrue(is_sparql_query("DESCRIBE <http://example.org/resource>"))
        
        # Test with natural language queries
        self.assertFalse(is_sparql_query("last 3 popes"))
        self.assertFalse(is_sparql_query("information about cats"))
    
    def test_enhanced_execute_wikidata_sparql(self):
        # Create a mock function for the original execute_wikidata_sparql
        original_function = MagicMock()
        original_function.return_value = '{"results": {"bindings": []}}'
        
        # Apply the decorator
        enhanced_function = enhanced_execute_wikidata_sparql(original_function)
        
        # Test with a SPARQL query
        result = enhanced_function("SELECT * WHERE { ?s ?p ?o }")
        original_function.assert_called_once_with("SELECT * WHERE { ?s ?p ?o }")
        
        # Verify that metadata is added to the result
        result_data = json.loads(result)
        self.assertIn("metadata", result_data)
        self.assertIn("current_date", result_data["metadata"])
        self.assertIn("query_processed_on", result_data["metadata"])
        self.assertEqual(result_data["metadata"]["query_type"], "sparql")
        
        # Reset the mock
        original_function.reset_mock()
        
        # Test with a natural language query
        with patch('orchestration.server_integration.process_natural_language_query') as mock_process:
            mock_process.return_value = '{"results": {"bindings": []}}'
            enhanced_function("last 3 popes")
            original_function.assert_not_called()
            mock_process.assert_called_once()
            args, _ = mock_process.call_args
            self.assertEqual(args[0], "last 3 popes")
            # The second argument should be the current date (default)
            self.assertIsInstance(args[1], datetime.date)
    
    def test_enhanced_execute_wikidata_sparql_with_custom_date(self):
        # Create a mock function for the original execute_wikidata_sparql
        original_function = MagicMock()
        original_function.return_value = '{"results": {"bindings": []}}'
        
        # Apply the decorator
        enhanced_function = enhanced_execute_wikidata_sparql(original_function)
        
        # Use a specific test date
        test_date = datetime.date(2023, 1, 1)
        
        # Test with a SPARQL query and custom date
        result = enhanced_function("SELECT * WHERE { ?s ?p ?o }", test_date)
        original_function.assert_called_once_with("SELECT * WHERE { ?s ?p ?o }")
        
        # Verify that metadata includes the custom date
        result_data = json.loads(result)
        self.assertIn("metadata", result_data)
        self.assertEqual(result_data["metadata"]["current_date"], test_date.isoformat())
        
        # Reset the mock
        original_function.reset_mock()
        
        # Test with a natural language query and custom date
        with patch('orchestration.server_integration.process_natural_language_query') as mock_process:
            mock_process.return_value = '{"results": {"bindings": []}}'
            enhanced_function("current pope", test_date)
            original_function.assert_not_called()
            mock_process.assert_called_once()
            args, _ = mock_process.call_args
            self.assertEqual(args[0], "current pope")
            self.assertEqual(args[1], test_date)

if __name__ == "__main__":
    unittest.main()
