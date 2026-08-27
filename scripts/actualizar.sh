#!/bin/bash
# Script de actualización de reportes procesos construcción Honduras
# Ejecuta extracción de datos y generación de reportes
# Soporta: ejecución automática + ejecución manual on-demand

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar header
show_header() {
    echo ""
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}🏗️  ACTUALIZACIÓN - PROCESOS CONSTRUCCIÓN HONDURAS${NC}"
    echo -e "${BLUE}===================================================${NC}"
    echo ""
}

# Función para mostrar menú (si se ejecuta sin argumentos)
show_menu() {
    echo -e "${YELLOW}Opciones de Ejecución:${NC}"
    echo ""
    echo "  ${GREEN}1${NC} - Extracción Completa (extractor + reportes + git)"
    echo "  ${GREEN}2${NC} - Solo Extracción de Datos (sin reportes ni git)"
    echo "  ${GREEN}3${NC} - Solo Generación de Reportes (sin extracción)"
    echo "  ${GREEN}4${NC} - Verificar Estado del Sistema"
    echo "  ${GREEN}5${NC} - Ver Últimas Extracciones"
    echo "  ${GREEN}0${NC} - Salir"
    echo ""
}

# Función para extracción de datos
extract_data() {
    echo -e "${BLUE}📥 Extrayendo datos de Honduras Compras...${NC}"
    python3 scripts/extractor_honduras_compras_v3.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Extracción completada${NC}"
        return 0
    else
        echo -e "${RED}❌ Error en extracción${NC}"
        return 1
    fi
}

# Función para generación de reportes
generate_reports() {
    echo ""
    echo -e "${BLUE}📊 Generando reportes HTML...${NC}"
    python3 scripts/generar_reportes.py

    echo ""
    echo -e "${BLUE}📋 Verificando archivos generados...${NC}"
    if [ -f "reportes/licitaciones.html" ] && [ -f "reportes/compras-menores.html" ]; then
        echo -e "${GREEN}✅ Reportes generados exitosamente:${NC}"
        echo "   • reportes/licitaciones.html ($(wc -c < reportes/licitaciones.html | numfmt --to=iec-i --suffix=B 2>/dev/null || echo 'N/A'))"
        echo "   • reportes/compras-menores.html ($(wc -c < reportes/compras-menores.html | numfmt --to=iec-i --suffix=B 2>/dev/null || echo 'N/A'))"
        return 0
    else
        echo -e "${RED}❌ Error: No todos los reportes fueron generados${NC}"
        return 1
    fi
}

# Función para sincronización con Git
sync_git() {
    echo ""
    echo -e "${BLUE}🔄 Sincronizando con Git...${NC}"
    git add data/ reportes/

    if git diff --cached --quiet; then
        echo -e "${YELLOW}ℹ️  No hay cambios para commit${NC}"
        return 0
    else
        CHANGES=$(git diff --cached --name-only | wc -l)
        git commit -m "🔄 Actualización on-demand de procesos construcción Honduras - $(date '+%Y-%m-%d %H:%M')"

        if git push origin claude/honduras-procurement-report-hv200y; then
            echo -e "${GREEN}✅ Git sincronizado ($CHANGES archivos)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Advertencia: Push a Git falló (posible red)${NC}"
            return 0  # No es error crítico
        fi
    fi
}

# Función para verificar estado
check_status() {
    echo ""
    echo -e "${BLUE}🔍 Estado del Sistema${NC}"
    echo ""

    # Verificar archivos
    echo -e "${YELLOW}Archivos Disponibles:${NC}"
    if [ -f "data/licitaciones.json" ]; then
        LICITACIONES=$(python3 -c "import json; data=json.load(open('data/licitaciones.json')); print(data['metadata']['total_procesos'])" 2>/dev/null || echo "?")
        echo "  ✅ data/licitaciones.json ($LICITACIONES procesos)"
    else
        echo "  ❌ data/licitaciones.json (no encontrado)"
    fi

    if [ -f "data/compras-menores.json" ]; then
        COMPRAS=$(python3 -c "import json; data=json.load(open('data/compras-menores.json')); print(data['metadata']['total_procesos'])" 2>/dev/null || echo "?")
        echo "  ✅ data/compras-menores.json ($COMPRAS procesos)"
    else
        echo "  ❌ data/compras-menores.json (no encontrado)"
    fi

    if [ -f "reportes/licitaciones.html" ]; then
        echo "  ✅ reportes/licitaciones.html"
    else
        echo "  ❌ reportes/licitaciones.html (no encontrado)"
    fi

    if [ -f "reportes/compras-menores.html" ]; then
        echo "  ✅ reportes/compras-menores.html"
    else
        echo "  ❌ reportes/compras-menores.html (no encontrado)"
    fi

    echo ""
    echo -e "${YELLOW}Rama Git:${NC}"
    git branch -v | grep '\*'

    echo ""
    echo -e "${YELLOW}Últimas Actualizaciones:${NC}"
    git log --oneline -3
}

# Función para ver historial
show_history() {
    echo ""
    echo -e "${YELLOW}Últimas 10 Actualizaciones:${NC}"
    git log --oneline -10 -- data/ reportes/ 2>/dev/null || echo "No hay historial"
}

# Verificar directorio raíz
if [ ! -f "CLAUDE.md" ]; then
    echo -e "${RED}❌ Error: Ejecutar desde el directorio raíz del proyecto${NC}"
    exit 1
fi

# Crear directorios si no existen
mkdir -p data
mkdir -p reportes

# Procesar argumentos o mostrar menú interactivo
if [ $# -eq 0 ]; then
    # Modo interactivo
    show_header
    show_menu
    read -p "Selecciona opción: " OPTION
else
    OPTION=$1
fi

case $OPTION in
    1)
        show_header
        echo -e "${GREEN}→ Extracción Completa Iniciada${NC}"
        echo ""

        extract_data || exit 1
        generate_reports || exit 1
        sync_git

        echo ""
        echo -e "${BLUE}===================================================${NC}"
        echo -e "${GREEN}✅ ACTUALIZACIÓN COMPLETADA${NC}"
        echo -e "${BLUE}===================================================${NC}"
        echo -e "${YELLOW}Estadísticas:${NC}"
        echo "  📅 Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "  📁 Reportes: reportes/"
        echo "  💾 Datos: data/"
        echo ""
        echo -e "${YELLOW}Próximas acciones:${NC}"
        echo "  1. Revisar: open reportes/licitaciones.html"
        echo "  2. Compartir: git log --oneline -1"
        echo ""
        ;;
    2)
        show_header
        echo -e "${GREEN}→ Solo Extracción de Datos${NC}"
        echo ""
        extract_data || exit 1
        echo -e "${GREEN}✅ Extracción completada sin sincronización${NC}"
        ;;
    3)
        show_header
        echo -e "${GREEN}→ Solo Generación de Reportes${NC}"
        echo ""
        generate_reports || exit 1
        echo -e "${GREEN}✅ Reportes generados sin sincronización${NC}"
        ;;
    4)
        show_header
        check_status
        ;;
    5)
        show_header
        show_history
        ;;
    0)
        echo -e "${YELLOW}Saliendo...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Opción no válida${NC}"
        show_menu
        exit 1
        ;;
esac

echo ""
