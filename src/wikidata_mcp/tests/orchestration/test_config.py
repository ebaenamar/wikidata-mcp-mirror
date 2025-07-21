import unittest
import json
import os

class TestConfig(unittest.TestCase):
    def test_config_exists(self):
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "orchestration", "wikidata_config.json"
        )
        self.assertTrue(os.path.exists(config_path), "El archivo de configuración debe existir")
        
    def test_config_valid_json(self):
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "orchestration", "wikidata_config.json"
        )
        with open(config_path, "r") as f:
            config = json.load(f)
        self.assertIn("signalTypes", config)
        self.assertIn("commonEntities", config)
        self.assertIn("queryPatterns", config)

if __name__ == "__main__":
    unittest.main()
