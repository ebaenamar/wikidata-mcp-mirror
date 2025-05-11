import unittest
import json
from orchestration.query_orchestrator import QueryOrchestrator

class TestQueryOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = QueryOrchestrator()
    
    def test_process_generic_query(self):
        # Procesar una consulta genérica
        result = self.orchestrator.process_query("información sobre gatos")
        
        # Verificar que se manejó como consulta genérica
        self.assertIn("warning", result)
        self.assertEqual(result["query_type"], "generic_query")
        
    def test_analyze_temporal_query(self):
        # Verificar que el analizador detecta correctamente una consulta temporal
        signal = self.orchestrator.analyzer.analyze("últimos 3 papas")
        self.assertEqual(signal.query_type, "temporal_query")
        self.assertEqual(signal.limit_constraints, 3)
        self.assertIn("Q9951", signal.entities)  # ID de "papa" en Wikidata

if __name__ == "__main__":
    unittest.main()
