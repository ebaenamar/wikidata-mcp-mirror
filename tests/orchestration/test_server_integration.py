import unittest
import json
from unittest.mock import patch, MagicMock
from orchestration.server_integration import is_sparql_query, enhanced_execute_wikidata_sparql

class TestServerIntegration(unittest.TestCase):
    def test_is_sparql_query(self):
        # Probar con consultas SPARQL
        self.assertTrue(is_sparql_query("SELECT * WHERE { ?s ?p ?o }"))
        self.assertTrue(is_sparql_query("ASK WHERE { ?s ?p ?o }"))
        self.assertTrue(is_sparql_query("CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }"))
        self.assertTrue(is_sparql_query("DESCRIBE <http://example.org/resource>"))
        
        # Probar con consultas en lenguaje natural
        self.assertFalse(is_sparql_query("últimos 3 papas"))
        self.assertFalse(is_sparql_query("información sobre gatos"))
    
    def test_enhanced_execute_wikidata_sparql(self):
        # Crear una función mock para el original execute_wikidata_sparql
        original_function = MagicMock()
        original_function.return_value = '{"results": {"bindings": []}}'
        
        # Aplicar el decorador
        enhanced_function = enhanced_execute_wikidata_sparql(original_function)
        
        # Probar con una consulta SPARQL
        enhanced_function("SELECT * WHERE { ?s ?p ?o }")
        original_function.assert_called_once_with("SELECT * WHERE { ?s ?p ?o }")
        
        # Reiniciar el mock
        original_function.reset_mock()
        
        # Probar con una consulta en lenguaje natural
        with patch('orchestration.server_integration.process_natural_language_query') as mock_process:
            mock_process.return_value = '{"results": {"bindings": []}}'
            enhanced_function("últimos 3 papas")
            original_function.assert_not_called()
            mock_process.assert_called_once_with("últimos 3 papas")

if __name__ == "__main__":
    unittest.main()
