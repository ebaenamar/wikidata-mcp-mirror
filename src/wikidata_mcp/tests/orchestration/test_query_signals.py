import unittest
import json
from orchestration.query_signals import QuerySignal

class TestQuerySignals(unittest.TestCase):
    def test_create_signal(self):
        signal = QuerySignal(
            query_type="temporal_query",
            entities=["Q9951"],
            limit_constraints=3,
            message="Consulta: últimos 3 papas"
        )
        self.assertEqual(signal.query_type, "temporal_query")
        self.assertEqual(signal.entities, ["Q9951"])
        self.assertEqual(signal.limit_constraints, 3)
        
    def test_signal_serialization(self):
        signal = QuerySignal(
            query_type="temporal_query",
            entities=["Q9951"],
            limit_constraints=3,
            message="Consulta: últimos 3 papas"
        )
        signal_dict = signal.to_dict()
        self.assertIn("id", signal_dict)
        self.assertIn("query_type", signal_dict)
        self.assertIn("entities", signal_dict)
        self.assertIn("limit_constraints", signal_dict)
        
        # Recrear seu00f1al desde diccionario
        recreated_signal = QuerySignal.from_dict(signal_dict)
        self.assertEqual(recreated_signal.id, signal.id)
        self.assertEqual(recreated_signal.query_type, signal.query_type)
        self.assertEqual(recreated_signal.entities, signal.entities)
        self.assertEqual(recreated_signal.limit_constraints, signal.limit_constraints)

if __name__ == "__main__":
    unittest.main()
