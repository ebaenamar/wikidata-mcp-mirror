import json
import os
import time
from typing import Dict, Any, Optional

class WikidataCache:
    def __init__(self, cache_file: str = None, evaporation_rate: float = 0.05):
        self.cache_file = cache_file or os.path.join(
            os.path.dirname(__file__), "wikidata_cache.json"
        )
        self.evaporation_rate = evaporation_rate
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict[str, Any]:
        """
        Carga la caché desde el archivo.
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except:
                return {"queries": {}, "last_cleanup": time.time()}
        return {"queries": {}, "last_cleanup": time.time()}
        
    def _save_cache(self) -> None:
        """
        Guarda la caché en el archivo.
        """
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)
        
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un resultado de la caché si existe y no ha expirado.
        """
        self._evaporate()
        
        query_hash = str(hash(query))
        if query_hash in self.cache["queries"]:
            entry = self.cache["queries"][query_hash]
            # Amplificar la entrada (aumentar su fuerza)
            entry["strength"] = min(1.0, entry["strength"] + 0.1)
            entry["access_count"] += 1
            entry["last_access"] = time.time()
            self._save_cache()
            return entry["result"]
        return None
        
    def set(self, query: str, result: Dict[str, Any]) -> None:
        """
        Guarda un resultado en la caché.
        """
        query_hash = str(hash(query))
        self.cache["queries"][query_hash] = {
            "query": query,
            "result": result,
            "timestamp": time.time(),
            "strength": 1.0,
            "access_count": 1,
            "last_access": time.time()
        }
        self._save_cache()
        
    def _evaporate(self) -> None:
        """
        Reduce la fuerza de las entradas de la caché con el tiempo.
        """
        current_time = time.time()
        # Ejecutar evaporación cada hora
        if current_time - self.cache["last_cleanup"] < 3600:
            return
            
        for query_hash, entry in list(self.cache["queries"].items()):
            # Reducir la fuerza basada en el tiempo desde el último acceso
            time_factor = (current_time - entry["last_access"]) / 86400  # Días
            entry["strength"] -= self.evaporation_rate * time_factor
            
            # Eliminar entradas débiles
            if entry["strength"] <= 0:
                del self.cache["queries"][query_hash]
        
        self.cache["last_cleanup"] = current_time
        self._save_cache()
