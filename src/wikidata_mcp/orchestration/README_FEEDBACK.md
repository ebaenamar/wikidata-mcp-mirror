# Sistema de Feedback de Lazo Cerrado para Consultas Fallidas

Este documento describe el sistema de feedback de lazo cerrado implementado para mejorar el manejo de consultas fallidas en el orquestador de consultas de Wikidata.

## Descripción General

El sistema de feedback de lazo cerrado permite que el orquestador de consultas aprenda de los errores y mejore con el tiempo, sin necesidad de intervención manual. Este sistema tiene tres componentes principales:

1. **Registro de Consultas Fallidas**: Almacena información sobre consultas que fallan, incluyendo el mensaje de error y el tipo de consulta.

2. **Corrección de Consultas**: Sugiere correcciones para consultas que han fallado previamente, basándose en patrones exitosos anteriores.

3. **Análisis de Patrones**: Identifica patrones comunes en las consultas fallidas y genera recomendaciones para mejorar el sistema.

## Componentes del Sistema

### 1. QueryFeedback

Clase principal que gestiona el registro y la corrección de consultas fallidas:

- `register_failed_query()`: Registra una consulta fallida con su mensaje de error.
- `register_correction()`: Registra una corrección exitosa o fallida para una consulta.
- `get_suggested_correction()`: Obtiene una corrección sugerida para una consulta basada en correcciones exitosas anteriores.

### 2. QueryOrchestrator (Integración)

El orquestador de consultas ha sido actualizado para utilizar el sistema de feedback:

- Intenta correcciones sugeridas para consultas que podrían fallar.
- Registra consultas fallidas para análisis futuro.
- Proporciona sugerencias de consultas similares cuando una consulta falla.

### 3. QueryFeedbackAnalysis

Clase para analizar los datos de feedback y generar informes:

- `generate_failure_report()`: Genera un informe detallado de patrones de fallo.
- `save_report()`: Guarda el informe para análisis posterior.

## Herramientas de Análisis

Se incluye una herramienta de línea de comandos para analizar las consultas fallidas:

```bash
python tools/analyze_failed_queries.py --format text --output report.txt
```

Esta herramienta genera un informe detallado que incluye:

- Patrones comunes en consultas fallidas
- Estadísticas de correcciones exitosas
- Recomendaciones para mejorar el sistema

## Cómo Funciona el Lazo Cerrado

1. **Detección**: Cuando una consulta falla, se registra en el sistema de feedback.

2. **Aprendizaje**: El sistema analiza patrones en las consultas fallidas y registra correcciones exitosas.

3. **Adaptación**: Cuando se recibe una consulta similar a una que falló anteriormente, el sistema intenta aplicar una corrección exitosa.

4. **Mejora Continua**: Con el tiempo, el sistema aprende qué correcciones funcionan mejor para diferentes tipos de consultas.

## Ejemplo de Uso

### Registro de una Consulta Fallida

Cuando una consulta falla, el sistema la registra automáticamente:

```python
# Esto ocurre internamente en el orquestador
feedback.register_failed_query("últimos 3 papas", "Error: No se pudo analizar la consulta temporal")
```

### Corrección Automática

Cuando se recibe una consulta similar a una que falló anteriormente:

```python
# Consulta original que falló: "últimos 3 papas"
# Nueva consulta similar: "últimos tres papas"
correction = feedback.get_suggested_correction("últimos tres papas")
# Podría devolver: "last 3 popes"
```

### Análisis de Patrones

Ejecutando la herramienta de análisis:

```bash
python tools/analyze_failed_queries.py
```

Podría mostrar que muchas consultas temporales fallan debido a problemas con el formato de fecha, lo que ayudaría a mejorar el sistema.

## Beneficios

- **Mejora Automática**: El sistema mejora con el tiempo sin intervención manual.
- **Adaptación a Patrones de Usuario**: Se adapta a los tipos de consultas más comunes.
- **Identificación de Problemas**: Ayuda a identificar áreas problemáticas en el procesamiento de consultas.
- **Sugerencias Útiles**: Proporciona sugerencias útiles cuando las consultas fallan.

## Próximos Pasos

1. Implementar análisis más avanzados de patrones de consulta utilizando NLP.
2. Desarrollar un sistema de retroalimentación directa del usuario.
3. Integrar el sistema con un mecanismo de aprendizaje automático para mejorar las predicciones de correcciones.
