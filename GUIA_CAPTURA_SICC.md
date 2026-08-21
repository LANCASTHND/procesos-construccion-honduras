# 📋 Guía: Capturar Datos Reales de SICC Honduras

## Problema
SICC carga datos dinámicamente con JavaScript. La extracción automatizada requiere conocer la estructura HTML exacta.

## Solución Rápida: Copy-Paste desde SICC

### Paso 1: Abre SICC
```
Dirección: http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx
```

### Paso 2: Selecciona la Tabla de Resultados
En SICC, verás una tabla con procesos vigentes. Selecciona toda la tabla (Ctrl+A dentro de la tabla).

### Paso 3: Copia los Datos
- Haz clic derecho → Copiar
- O: Ctrl+C

### Paso 4: Pega en `data/PLANTILLA_IMPORTAR.csv`
```bash
# Opción A: Editor de texto
nano data/PLANTILLA_IMPORTAR.csv
# Pega los datos

# Opción B: Comando directo
cat > data/PLANTILLA_IMPORTAR.csv << 'EOF'
[PEGA AQUÍ LOS DATOS DE SICC]
EOF
```

### Paso 5: Ejecuta el Importador
```bash
python3 scripts/importar_desde_csv.py
python3 scripts/generar_reportes.py
```

### Paso 6: Abre los Reportes
```bash
open reportes/licitaciones.html
```

---

## Solución Alternativa: Actualización Diaria Automática

### 1. Exporta datos de SICC cada mañana
2. Los pegasen `data/PLANTILLA_IMPORTAR.csv`
3. Ejecuta el importador

### 2. O configura una Rutina Automática
```
/schedule

Nombre: Actualizar procesos Honduras SICC
Prompt: 
  python3 scripts/importar_desde_csv.py
  python3 scripts/generar_reportes.py

Cron: 0 6 * * *  (6:00 AM Honduras = 12:00 PM UTC)
```

---

## Formato CSV Esperado

```csv
expediente,descripcion,institucion,monto,cierre,contacto,link,tipo_licitacion
LPN No. 08-2026-SEAPI-UNAH,Mejoramiento Edificio,UNAH,25000000,20/10/2026,unah-compras@unah.edu.hn,http://sicc...,licitacion_normal
Construcción Hospital,Construcción Hospital,SESALUD,45000000,13/10/2026,compras@sesalud.gob.hn,http://sicc...,licitacion_normal
```

### Columnas Requeridas:
- **expediente**: Código del proceso
- **descripcion**: Descripción del proyecto
- **institucion**: UNAH, SIT, UNA, SESALUD, etc.
- **monto**: Número sin L. ni comas (ej: 25000000)
- **cierre**: Fecha DD/MM/YYYY
- **contacto**: email@ejemplo.hn
- **link**: URL del proceso en SICC
- **tipo_licitacion**: licitacion_normal o compra_menor

---

## Verificar Datos Importados

```bash
# Ver JSON generado
cat data/licitaciones.json

# Ver reportes HTML
open reportes/licitaciones.html
open reportes/compras-menores.html
```

---

## Troubleshooting

### "No se importaron procesos"
- Verifica que las fechas estén en formato DD/MM/YYYY
- Verifica que no haya procesos ya cerrados (fecha en pasado)
- Verifica que los montos sean números válidos

### "El reporte no muestra datos"
- Verifica que data/licitaciones.json tenga contenido
- Regenera reportes: `python3 scripts/generar_reportes.py`

### "¿Cómo obtener todos los procesos de SICC?"
- Ve a SICC con búsqueda sin filtros (vacío)
- Dale "Buscar"
- Selecciona toda la tabla de resultados
- Copia y pega en PLANTILLA_IMPORTAR.csv

---

##Workflow Completo

```bash
# 1. Importar datos reales desde SICC
python3 scripts/importar_desde_csv.py

# 2. Generar reportes HTML
python3 scripts/generar_reportes.py

# 3. Ver reportes
open reportes/licitaciones.html

# 4. Sincronizar con Git (opcional)
git add data/ reportes/
git commit -m "Actualizar procesos SICC $(date +%Y-%m-%d)"
git push origin claude/honduras-procurement-report-hv200y
```

---

## Próximo Paso: API de SICC

Si SICC expone una API JSON, podríamos automatizar completamente esto.
**Solicitado**: Información sobre API SICC Honduras Compras.

