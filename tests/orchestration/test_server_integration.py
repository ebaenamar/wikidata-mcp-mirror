import unittest
import json
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
        enhanced_function("SELECT * WHERE { ?s ?p ?o }")
        original_function.assert_called_once_with("SELECT * WHERE { ?s ?p ?o }")
        
        # Reset the mock
        original_function.reset_mock()
        
        # Test with a natural language query
        with patch('orchestration.server_integration.process_natural_language_query') as mock_process:
            mock_process.return_value = '{"results": {"bindings": []}}'
            enhanced_function("last 3 popes")
            original_function.assert_not_called()
            mock_process.assert_called_once_with("last 3 popes")

if __name__ == "__main__":
    unittest.main()
