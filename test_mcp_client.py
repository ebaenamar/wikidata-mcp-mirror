#!/usr/bin/env python3
"""
Script simple para probar la conexión MCP con SSE
"""
import requests
import json
import time
import threading
import sseclient

# URL del servidor MCP
SERVER_URL = "https://wikidata-mcp.onrender.com"

def listen_sse():
    """Escucha eventos SSE del servidor"""
    print(f"Conectando a {SERVER_URL}/sse...")
    headers = {'Accept': 'text/event-stream'}
    response = requests.get(f"{SERVER_URL}/sse", headers=headers, stream=True)
    client = sseclient.SSEClient(response)
    
    session_id = None
    
    for event in client.events():
        print(f"Evento recibido: {event.event}")
        print(f"Datos: {event.data}")
        
        if event.event == 'endpoint':
            # Extraer el ID de sesión de la URL
            endpoint = event.data
            session_id = endpoint.split('session_id=')[1]
            print(f"ID de sesión recibido: {session_id}")
            
            # Enviar mensaje de inicialización
            send_initialize(session_id)
        
        # Si recibimos una respuesta a nuestra inicialización, salir
        if session_id and 'result' in event.data:
            print("Inicialización completada con éxito")
            break

def send_initialize(session_id):
    """Envía un mensaje de inicialización al servidor"""
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
    response = requests.post(
        f"{SERVER_URL}/messages?session_id={session_id}",
        headers=headers,
        data=json.dumps(init_message)
    )
    
    print(f"Respuesta del servidor: {response.status_code}")
    if response.status_code != 200:
        print(f"Contenido de la respuesta: {response.text}")

if __name__ == "__main__":
    # Instalar dependencias si es necesario
    try:
        import sseclient
    except ImportError:
        print("Instalando dependencias...")
        import subprocess
        subprocess.check_call(["pip", "install", "sseclient-py"])
        import sseclient
    
    # Ejecutar el cliente
    listen_sse()
