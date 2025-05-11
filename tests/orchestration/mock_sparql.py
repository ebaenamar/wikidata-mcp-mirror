def mock_execute_sparql(sparql_query: str) -> str:
    """
    Mock para pruebas que simula la ejecuciu00f3n de consultas SPARQL.
    """
    if "wd:Q9951" in sparql_query and "LIMIT 3" in sparql_query:
        # Simular resultados para "u00faltimos 3 papas"
        return """
        {
          "head": {
            "vars": [ "item", "itemLabel", "startDate", "endDate" ]
          },
          "results": {
            "bindings": [
              {
                "item": { "type": "uri", "value": "http://www.wikidata.org/entity/Q450675" },
                "itemLabel": { "type": "literal", "value": "Francisco" },
                "startDate": { "type": "literal", "value": "2013-03-13T00:00:00Z" }
              },
              {
                "item": { "type": "uri", "value": "http://www.wikidata.org/entity/Q2494" },
                "itemLabel": { "type": "literal", "value": "Benedicto XVI" },
                "startDate": { "type": "literal", "value": "2005-04-19T00:00:00Z" },
                "endDate": { "type": "literal", "value": "2013-02-28T00:00:00Z" }
              },
              {
                "item": { "type": "uri", "value": "http://www.wikidata.org/entity/Q989" },
                "itemLabel": { "type": "literal", "value": "Juan Pablo II" },
                "startDate": { "type": "literal", "value": "1978-10-16T00:00:00Z" },
                "endDate": { "type": "literal", "value": "2005-04-02T00:00:00Z" }
              }
            ]
          }
        }
        """
    return '{"error": "Consulta no soportada en el mock"}'
