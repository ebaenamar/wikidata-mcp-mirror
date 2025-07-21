import unittest
import json
from orchestration.query_signals import QuerySignal
from orchestration.temporal_specialist import TemporalSpecialist
from tests.orchestration.mock_sparql import mock_execute_sparql

class TestTemporalSpecialist(unittest.TestCase):
    def setUp(self):
        self.specialist = TemporalSpecialist(sparql_executor=mock_execute_sparql)
    
    def test_handle_papal_query(self):
        signal = QuerySignal(
            query_type="temporal_query",
            entities=["Q9951"],  # Papa
            limit_constraints=3,
            message="Consulta: últimos 3 papas"
        )
        
        result = self.specialist.handle_query(signal)
        self.assertIn("results", result)
        self.assertIn("bindings", result["results"])
        
        # Verificar que tenemos 3 papas en los resultados
        bindings = result["results"]["bindings"]
        self.assertEqual(len(bindings), 3)
        
        # Verificar que Francisco está en los resultados
        found_francisco = False
        for binding in bindings:
            if "itemLabel" in binding and binding["itemLabel"]["value"] == "Francisco":
                found_francisco = True
                break
        self.assertTrue(found_francisco, "Francisco debe estar en los resultados")
    
    def test_handle_unsupported_query(self):
        signal = QuerySignal(
            query_type="temporal_query",
            entities=["Q42"],  # No es papa
            limit_constraints=3,
            message="Consulta no soportada"
        )
        
        result = self.specialist.handle_query(signal)
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()
