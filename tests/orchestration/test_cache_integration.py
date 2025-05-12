import unittest
import os
import json
from orchestration.query_orchestrator import QueryOrchestrator

class TestCacheIntegration(unittest.TestCase):
    def setUp(self):
        # Crear un archivo de caché temporal para las pruebas
        self.temp_cache_file = "/tmp/test_orchestrator_cache.json"
        if os.path.exists(self.temp_cache_file):
            os.remove(self.temp_cache_file)
        
        # Inicializar el orquestador con caché
        self.orchestrator = QueryOrchestrator(use_cache=True)
        # Establecer el archivo de caché temporal
        self.orchestrator.cache.cache_file = self.temp_cache_file
    
    def tearDown(self):
        # Limpiar después de las pruebas
        if os.path.exists(self.temp_cache_file):
            os.remove(self.temp_cache_file)
    
    def test_cache_hit_miss(self):
        # Primera consulta (miss de caché)
        query = "información sobre gatos"
        result1 = self.orchestrator.process_query(query)
        
        # Verificar que se guardó en caché
        self.assertTrue(os.path.exists(self.temp_cache_file))
        
        # Crear un nuevo orquestador con la misma caché
        new_orchestrator = QueryOrchestrator(use_cache=True)
        new_orchestrator.cache.cache_file = self.temp_cache_file
        
        # Segunda consulta (hit de caché)
        result2 = new_orchestrator.process_query(query)
        
        # Verificar que los resultados son iguales, ignorando campos dinámicos como timestamps
        # Eliminar los campos dinámicos antes de comparar
        if 'metadata' in result1 and 'query_processed_on' in result1['metadata']:
            del result1['metadata']['query_processed_on']
        if 'metadata' in result2 and 'query_processed_on' in result2['metadata']:
            del result2['metadata']['query_processed_on']
            
        self.assertEqual(result1, result2)
    
    def test_cache_disabled(self):
        # Crear un orquestador sin caché
        no_cache_orchestrator = QueryOrchestrator(use_cache=False)
        
        # Ejecutar una consulta
        query = "últimos 3 papas"
        no_cache_orchestrator.process_query(query)
        
        # Verificar que no se creó un archivo de caché
        self.assertFalse(hasattr(no_cache_orchestrator, "cache"))

if __name__ == "__main__":
    unittest.main()
