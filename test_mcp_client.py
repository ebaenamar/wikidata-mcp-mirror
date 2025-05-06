#!/usr/bin/env python3
"""
Script para probar la conexión MCP con SSE, replicando el comportamiento del cliente de Claude
"""
import requests
import json
import time
import threading
import sseclient
import sys

# URL del servidor MCP
SERVER_URL = "https://wikidata-mcp.onrender.com"

def try_http_first():
    """Intenta la estrategia http-first"""
    print("Usando estrategia: http-first")
    
    # Primero intentamos enviar un mensaje POST sin establecer una conexión SSE
    init_message = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "0.1.0"
            }
        },
        "id": 0
    }
    
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(
            f"{SERVER_URL}/messages",
            headers=headers,
            data=json.dumps(init_message),
            timeout=5
        )
        
        print(f"Respuesta HTTP-first: {response.status_code}")
        print(f"Contenido de la respuesta: {response.text}")
        
        if response.status_code == 200:
            print("Estrategia http-first exitosa")
            return True
        else:
            print("Estrategia http-first fallida, cambiando a sse-only")
            return False
    except Exception as e:
        print(f"Error en http-first: {e}")
        return False

def try_sse_only():
    """Intenta la estrategia sse-only"""
    print("Usando estrategia: sse-only")
    
    try:
        # Establecer conexión SSE
        print(f"Conectando a {SERVER_URL}/sse...")
        headers = {'Accept': 'text/event-stream'}
        response = requests.get(f"{SERVER_URL}/sse", headers=headers, stream=True, timeout=10)
        
        if response.status_code != 200:
            print(f"Error al conectar SSE: {response.status_code}")
            print(f"Contenido: {response.text}")
            return False
            
        client = sseclient.SSEClient(response)
        
        session_id = None
        
        # Esperar el evento endpoint con el ID de sesión
        for event in client.events():
            print(f"Evento recibido: {event.event}")
            print(f"Datos: {event.data}")
            
            if event.event == 'endpoint':
                # Extraer el ID de sesión de la URL
                endpoint = event.data
                if 'session_id=' in endpoint:
                    session_id = endpoint.split('session_id=')[1]
                    print(f"ID de sesión recibido: {session_id}")
                    break
                else:
                    print("No se encontró session_id en el endpoint")
                    return False
        
        if not session_id:
            print("No se recibió ID de sesión")
            return False
            
        # Enviar mensaje de inicialización con el ID de sesión
        print(f"Enviando mensaje de inicialización con ID de sesión: {session_id}")
        
        init_message = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "0.1.0"
                }
            },
            "id": 0
        }
        
        headers = {'Content-Type': 'application/json'}
        init_response = requests.post(
            f"{SERVER_URL}/messages?session_id={session_id}",
            headers=headers,
            data=json.dumps(init_message),
            timeout=5
        )
        
        print(f"Respuesta del servidor: {init_response.status_code}")
        print(f"Contenido de la respuesta: {init_response.text}")
        
        # También probar con la ruta con barra final
        print("Probando con ruta con barra final...")
        init_response = requests.post(
            f"{SERVER_URL}/messages/?session_id={session_id}",
            headers=headers,
            data=json.dumps(init_message),
            timeout=5
        )
        
        print(f"Respuesta del servidor (con barra final): {init_response.status_code}")
        print(f"Contenido de la respuesta: {init_response.text}")
        
        return init_response.status_code in [200, 202]
        
    except Exception as e:
        print(f"Error en sse-only: {e}")
        return False

if __name__ == "__main__":
    # Instalar dependencias si es necesario
    try:
        import sseclient
    except ImportError:
        print("Instalando dependencias...")
        import subprocess
        subprocess.check_call(["pip", "install", "sseclient-py"])
        import sseclient
    
    # Primero intentar http-first
    if try_http_first():
        print("Conexión exitosa con http-first")
        sys.exit(0)
    
    # Si falla, intentar sse-only
    print("Cambiando a estrategia sse-only...")
    if try_sse_only():
        print("Conexión exitosa con sse-only")
        sys.exit(0)
    else:
        print("Ambas estrategias fallaron")
        sys.exit(1)
