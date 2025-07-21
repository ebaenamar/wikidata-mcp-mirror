import requests
import json
import time
import sys

def test_mcp_query(query_text):
    """
    Prueba una consulta en lenguaje natural al servidor MCP.
    """
    # URL del servidor MCP
    url = "http://localhost:8000/sse"
    
    # Cabeceras para la conexión SSE
    headers = {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache"
    }
    
    # Conectar al servidor SSE
    print(f"Conectando al servidor MCP en {url}...")
    response = requests.get(url, headers=headers, stream=True)
    
    if response.status_code != 200:
        print(f"Error al conectar: {response.status_code}")
        return
    
    print("Conexión establecida. Esperando inicialización...")
    time.sleep(2)  # Esperar a que se inicialice la conexión
    
    # Enviar la consulta al servidor
    print(f"Enviando consulta: '{query_text}'")
    
    # Construir el mensaje para el servidor MCP
    message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "execute",
        "params": {
            "name": "execute_wikidata_sparql",
            "parameters": {
                "sparql_query": query_text
            }
        }
    }
    
    # Enviar el mensaje al servidor
    requests.post(
        "http://localhost:8000/messages/",
        json=message,
        headers={"Content-Type": "application/json"}
    )
    
    # Procesar la respuesta del servidor
    print("Esperando respuesta...")
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data:'):
                data = line[5:].strip()
                if data:
                    try:
                        event = json.loads(data)
                        if 'result' in event:
                            print("\nRespuesta recibida:")
                            result = event['result']
                            print(json.dumps(result, indent=2, ensure_ascii=False))
                            return result
                    except json.JSONDecodeError:
                        print(f"Error al decodificar JSON: {data}")

if __name__ == "__main__":
    # Tomar la consulta de los argumentos de la línea de comandos
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "últimos 3 papas"
    test_mcp_query(query)
