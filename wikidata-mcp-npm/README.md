# Wikidata MCP para Claude Desktop

Este paquete proporciona acceso a Wikidata a través del Model Context Protocol (MCP) para Claude Desktop.

## ¿Qué es esto?

Este paquete permite a Claude Desktop conectarse a un servidor MCP de Wikidata, lo que le da a Claude la capacidad de:

- Buscar entidades y propiedades en Wikidata
- Obtener metadatos de entidades
- Ejecutar consultas SPARQL
- Acceder a información estructurada sobre millones de conceptos

## Opciones de instalación

Hay dos formas de configurar Claude Desktop para usar nuestro servidor Wikidata MCP:

### Opción 1: Configuración directa (Recomendada)

Esta opción no requiere instalar nuestro paquete npm. Simplemente configura Claude Desktop para usar el paquete `mcp-remote` para conectarse directamente a nuestro servidor.

1. Asegúrate de tener [Node.js](https://nodejs.org) instalado en tu computadora.

2. Edita el archivo de configuración de Claude Desktop:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

3. Reemplaza el contenido del archivo con:

```json
{
  "mcp": {
    "command": "npx",
    "args": [
      "mcp-remote",
      "--url",
      "https://wikidata-mcp.onrender.com/sse"
    ]
  }
}
```

4. Reinicia Claude Desktop.

### Opción 2: Usando nuestro paquete npm

Si prefieres usar nuestro paquete npm, sigue estos pasos:

1. Instala nuestro paquete globalmente:
   ```bash
   npm install -g wikidata-mcp
   ```

2. Edita el archivo de configuración de Claude Desktop:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

3. Reemplaza el contenido del archivo con:

```json
{
  "mcp": {
    "command": "wikidata-mcp"
  }
}
```

4. Reinicia Claude Desktop.

## Solución de problemas

Si tienes problemas para conectarte al servidor Wikidata MCP, prueba lo siguiente:

1. Asegúrate de tener la última versión de Claude Desktop.
2. Verifica que Node.js esté instalado correctamente ejecutando `node --version` en tu terminal.
3. Verifica la sintaxis de tu archivo `claude_desktop_config.json`.
4. Reinicia completamente Claude Desktop.
5. Revisa los logs de Claude Desktop:
   - macOS: `~/Library/Logs/Claude/mcp*.log`
   - Windows: `%APPDATA%\Claude\logs\mcp*.log`

## Licencia

MIT
