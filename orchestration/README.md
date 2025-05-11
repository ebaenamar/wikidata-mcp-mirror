# Sistema de Orquestación de Consultas para Wikidata MCP

Este sistema implementa un orquestador de consultas para el servidor MCP de Wikidata, permitiendo procesar consultas en lenguaje natural y convertirlas en consultas SPARQL estructuradas.

## Componentes Principales

### 1. Configuración (wikidata_config.json)

Archivo de configuración que define:
- Tipos de señales
- Entidades comunes
- Patrones de consulta
- Plantillas SPARQL

### 2. Señales de Consulta (query_signals.py)

Clase que representa consultas estructuradas con metadatos como:
- Tipo de consulta
- Entidades
- Restricciones temporales
- Límites

### 3. Analizador de Consultas (query_analyzer.py)

Convierte consultas en lenguaje natural en señales estructuradas mediante:
- Detección de palabras clave
- Identificación de entidades
- Reconocimiento de patrones temporales

### 4. Especialistas

#### Especialista Temporal (temporal_specialist.py)

Maneja consultas relacionadas con el tiempo, como:
- Eventos históricos
- Secuencias temporales
- Fechas específicas

### 5. Orquestador (query_orchestrator.py)

Coordina el proceso de consulta:
1. Recibe consultas en lenguaje natural
2. Utiliza el analizador para crear señales
3. Delega a especialistas según el tipo de consulta
4. Utiliza caché para mejorar el rendimiento

### 6. Sistema de Caché (wikidata_cache.py)

Almacena resultados de consultas con un mecanismo de evaporación:
- Guarda consultas con su fuerza inicial (1.0)
- Reduce la fuerza con el tiempo
- Elimina entradas cuando la fuerza llega a 0

### 7. Integración con el Servidor MCP

#### Módulo de Integración (mcp_integration.py)

Proporciona funciones para integrar el orquestador con el servidor MCP existente.

#### Integración del Servidor (server_integration.py)

Decorador que mejora la función `execute_wikidata_sparql` para manejar consultas en lenguaje natural.

## Uso

### Procesamiento de Consultas

```python
from orchestration.mcp_integration import process_natural_language_query

# Procesar una consulta en lenguaje natural
resultado = process_natural_language_query("últimos 3 papas")
print(resultado)
```

### Integración con el Servidor MCP

```python
from orchestration.server_integration import enhanced_execute_wikidata_sparql

# Mejorar la función execute_wikidata_sparql existente
execute_wikidata_sparql = enhanced_execute_wikidata_sparql(execute_wikidata_sparql)
```

## Pruebas

El sistema incluye pruebas unitarias y de integración para todos los componentes:

```bash
python -m unittest discover tests/orchestration
```
