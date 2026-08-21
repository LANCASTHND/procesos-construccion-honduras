#!/bin/bash
# Script de actualización de reportes procesos construcción Honduras
# Ejecuta extracción de datos y generación de reportes

set -e

echo "=================================================="
echo "🏗️  ACTUALIZACIÓN - PROCESOS CONSTRUCCIÓN HONDURAS"
echo "=================================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "CLAUDE.md" ]; then
    echo "❌ Error: Ejecutar desde el directorio raíz del proyecto"
    exit 1
fi

# Crear directorios si no existen
mkdir -p data
mkdir -p reportes

echo "📥 Paso 1: Extrayendo datos de Honduras Compras..."
python3 scripts/extractor_honduras_compras.py

echo ""
echo "📊 Paso 2: Generando reportes HTML..."
python3 scripts/generar_reportes.py

echo ""
echo "📋 Paso 3: Verificando archivos generados..."
if [ -f "reportes/licitaciones.html" ] && [ -f "reportes/compras-menores.html" ]; then
    echo "✅ Reportes generados exitosamente:"
    echo "   • reportes/licitaciones.html"
    echo "   • reportes/compras-menores.html"
else
    echo "⚠️  Advertencia: No todos los reportes fueron generados"
    exit 1
fi

echo ""
echo "🔄 Paso 4: Sincronizando con Git..."
git add data/ reportes/
if git diff --cached --quiet; then
    echo "ℹ️  No hay cambios para commit"
else
    git commit -m "🔄 Actualización automática de reportes procesos construcción Honduras"
    git push origin claude/honduras-procurement-report-hv200y
    echo "✅ Cambios sincronizados con Git"
fi

echo ""
echo "=================================================="
echo "✅ ACTUALIZACIÓN COMPLETADA"
echo "=================================================="
echo "⏰ Fecha: $(date)"
echo "📁 Reportes disponibles en: reportes/"
echo ""
echo "Próximas acciones:"
echo "  1. Verificar reportes en navegador: open reportes/licitaciones.html"
echo "  2. Compartir links de reportes con equipo"
echo "  3. Programar próxima actualización"
echo ""
