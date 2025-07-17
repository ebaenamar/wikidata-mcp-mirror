import unittest
import json
import os
import time
from unittest.mock import patch
from orchestration.wikidata_cache import WikidataCache

class TestWikidataCache(unittest.TestCase):
    def setUp(self):
        # Usar un archivo de caché temporal para las pruebas
        self.temp_cache_file = "/tmp/test_wikidata_cache.json"
        if os.path.exists(self.temp_cache_file):
            os.remove(self.temp_cache_file)
        self.cache = WikidataCache(cache_file=self.temp_cache_file)
    
    def tearDown(self):
        # Limpiar después de las pruebas
        if os.path.exists(self.temp_cache_file):
            os.remove(self.temp_cache_file)
    
    def test_cache_set_get(self):
        # Guardar un resultado en la caché
        test_query = "últimos 3 papas"
        test_result = {"results": {"bindings": [{"itemLabel": {"value": "Francisco"}}]}}
        self.cache.set(test_query, test_result)
        
        # Obtener el resultado de la caché
        cached_result = self.cache.get(test_query)
        self.assertEqual(cached_result, test_result)
    
    def test_cache_miss(self):
        # Intentar obtener un resultado que no está en la caché
        cached_result = self.cache.get("consulta no existente")
        self.assertIsNone(cached_result)
    
    def test_cache_strength_reduction(self):
        # Crear una instancia de caché con un archivo temporal
        temp_cache_file = "/tmp/test_wikidata_cache_strength.json"
        if os.path.exists(temp_cache_file):
            os.remove(temp_cache_file)
        
        # Crear una caché con una tasa de evaporación alta para pruebas
        cache = WikidataCache(cache_file=temp_cache_file, evaporation_rate=0.5)
        
        # Guardar un resultado en la caché
        test_query = "consulta de prueba"
        test_result = {"results": {"bindings": []}}
        cache.set(test_query, test_result)
        
        # Verificar que la entrada está en la caché
        query_hash = str(hash(test_query))
        self.assertIn(query_hash, cache.cache["queries"])
        self.assertEqual(cache.cache["queries"][query_hash]["strength"], 1.0)
        
        # Modificar manualmente la fuerza para simular la evaporación
        cache.cache["queries"][query_hash]["strength"] = 0.1
        cache._save_cache()
        
        # Verificar que la fuerza se redujo
        self.assertEqual(cache.cache["queries"][query_hash]["strength"], 0.1)
        
        # Limpiar
        if os.path.exists(temp_cache_file):
            os.remove(temp_cache_file)

if __name__ == "__main__":
    unittest.main()
