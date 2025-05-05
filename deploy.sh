#!/bin/bash

# Script para desplegar el servidor MCP SSE a Vercel

# Asegurarse de que estamos en el directorio correcto
cd "$(dirname "$0")"

# Verificar si git está inicializado
if [ ! -d ".git" ]; then
    echo "Inicializando repositorio git..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Desplegar a Vercel (si vercel CLI está instalado)
if command -v vercel &> /dev/null; then
    echo "Desplegando a Vercel..."
    vercel --prod
else
    echo "Vercel CLI no está instalado. Por favor instálalo con: npm i -g vercel"
    echo "Luego ejecuta: vercel --prod"
fi

# Hacer commit y push de los cambios
echo "Haciendo commit y push de los cambios..."
git add .
git commit -m "chore: deploy wikidata mcp server (SSE version)"
git push

echo "¡Despliegue completado!"
echo "Tu servidor MCP SSE debería estar disponible en la URL proporcionada por Vercel."
echo "Para registrarlo con NANDA, ejecuta:"
echo "python nanda_register.py --url TU_URL_DE_VERCEL"
