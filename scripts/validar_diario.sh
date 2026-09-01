#!/bin/bash
# Validación diaria: regenera reportes y detecta cambios

echo "================================"
echo "🔄 VALIDACIÓN DIARIA - $(date)"
echo "================================"
echo ""

# Regenerar reportes
echo "📊 Regenerando reportes..."
python3 scripts/generar_reportes.py > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Reportes regenerados"
else
    echo "❌ Error regenerando reportes"
    exit 1
fi

echo ""

# Contar procesos actuales
LIC_COUNT=$(jq '.metadata.total_procesos' data/licitaciones.json)
CM_COUNT=$(jq '.metadata.total_procesos' data/compras-menores.json)
TOTAL=$((LIC_COUNT + CM_COUNT))

echo "📈 Procesos vigentes:"
echo "   Licitaciones: $LIC_COUNT"
echo "   Compras menores: $CM_COUNT"
echo "   TOTAL: $TOTAL"
echo ""

# Git status
if git status --porcelain | grep -q .; then
    echo "📝 Cambios detectados en reportes"
    echo ""

    # Commit cambios
    git add reportes/*.html data/*.json
    git commit -m "Validación diaria: reportes actualizados - $TOTAL procesos vigentes"
    git push origin claude/honduras-procurement-report-hv200y

    echo "✅ Cambios commiteados y pusheados"
else
    echo "✅ Sin cambios en reportes (datos consistentes)"
fi

echo ""
echo "✅ Validación completada"
