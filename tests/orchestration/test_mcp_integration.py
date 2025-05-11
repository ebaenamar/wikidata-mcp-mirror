import unittest
import json
from unittest.mock import patch
from orchestration.mcp_integration import process_natural_language_query

class TestMCPIntegration(unittest.TestCase):
    @patch('orchestration.query_orchestrator.QueryOrchestrator.process_query')
    def test_process_natural_language_query(self, mock_process_query):
        # Configurar el mock para devolver un resultado simulado
        mock_result = {
            "results": {
                "bindings": [
                    {"itemLabel": {"value": "Francisco"}},
                    {"itemLabel": {"value": "Benedicto XVI"}},
                    {"itemLabel": {"value": "Juan Pablo II"}}
                ]
            }
        }
        mock_process_query.return_value = mock_result
        
        # Procesar una consulta
        result_json = process_natural_language_query("últimos 3 papas")
        result = json.loads(result_json)
        
        # Verificar que se llamó al orquestador
        mock_process_query.assert_called_once_with("últimos 3 papas")
        
        # Verificar que el resultado es el esperado
        self.assertEqual(result, mock_result)
    
    @patch('orchestration.query_orchestrator.QueryOrchestrator.process_query')
    def test_process_query_with_error(self, mock_process_query):
        # Configurar el mock para lanzar una excepción
        mock_process_query.side_effect = Exception("Error de prueba")
        
        # Procesar una consulta que generará un error
        result_json = process_natural_language_query("consulta con error")
        result = json.loads(result_json)
        
        # Verificar que se manejó el error correctamente
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()
