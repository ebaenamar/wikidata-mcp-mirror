import json
import os
from typing import Dict, Any, Optional
from .query_signals import QuerySignal

class TemporalSpecialist:
    def __init__(self, config_path: str = None, sparql_executor=None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "wikidata_config.json"
        )
        with open(self.config_path, "r") as f:
            self.config = json.load(f)
        
        # Usar el ejecutor proporcionado o crear una función dummy para las pruebas
        if sparql_executor is None:
            # En un entorno real, importaríamos wikidata_api.execute_sparql
            # Pero para las pruebas, usamos una función dummy que devuelve un error
            self.execute_sparql = lambda query: '{"error": "No se proporcionó un ejecutor SPARQL real"}'
        else:
            self.execute_sparql = sparql_executor
    
    def handle_query(self, signal: QuerySignal) -> Dict[str, Any]:
        """
        Maneja consultas con restricciones temporales.
        """
        # Ejemplo: "últimos 3 papas"
        if "Q9951" in signal.entities and signal.limit_constraints:  # Papa
            pattern = self.config["queryPatterns"]["last_n_position_holders"]
            sparql = pattern["sparqlTemplate"].format(
                position="Q9951",  # Papa
                limit=signal.limit_constraints
            )
            try:
                result = self.execute_sparql(sparql)
                return json.loads(result) if isinstance(result, str) else result
            except Exception as e:
                return {"error": f"Error al ejecutar la consulta SPARQL: {str(e)}"}
        
        # Implementar más casos...
        return {"error": "No se pudo procesar la consulta temporal"}
