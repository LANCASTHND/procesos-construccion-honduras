# 🏗️ Scripts de Actualización - Procesos Construcción Honduras

Conjunto de herramientas para extraer datos reales de procesos de licitación de Honduras Compras (SICC) y generar reportes interactivos.

---

## 📋 Descripción de Scripts

### 1. `extractor_honduras_compras.py`
**Extrae datos reales del SICC de Honduras Compras**

- Accede a: `http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx`
- Extrae:
  - Licitaciones normales (procesos de mayor cuantía)
  - Compras menores (procesos de menor cuantía)
  - Campos: expediente, descripción, institución, monto, cierre, contacto, link
- Genera archivos JSON en `data/`

**Uso:**
```bash
python3 scripts/extractor_honduras_compras.py
```

**Salida:**
- `data/licitaciones.json` - Procesos de licitación normal
- `data/compras-menores.json` - Procesos de compras menores

---

### 2. `generar_reportes.py`
**Crea reportes HTML interactivos a partir de datos JSON**

- Lee archivos JSON
- Genera tablas interactivas con:
  - Búsqueda por expediente
  - Filtro por institución
  - Links clickeables a contactos y SICC
  - Estadísticas de inversión
  - Diseño responsive

**Uso:**
```bash
python3 scripts/generar_reportes.py
```

**Salida:**
- `reportes/licitaciones.html` - Reporte licitaciones normales
- `reportes/compras-menores.html` - Reporte compras menores

---

### 3. `actualizar.sh`
**Script orquestador que ejecuta el flujo completo**

Ejecuta en orden:
1. Extrae datos de Honduras Compras
2. Genera reportes HTML
3. Sincroniza cambios con Git
4. Muestra resumen de actualización

**Uso:**
```bash
bash scripts/actualizar.sh
```

---

## 🚀 Instalación y Dependencias

### Requisitos
- Python 3.7+
- pip (gestor de paquetes)
- Git configurado
- Conexión a internet

### Instalar dependencias
```bash
pip install requests beautifulsoup4
```

O usando requirements.txt:
```bash
pip install -r scripts/requirements.txt
```

---

## 📊 Estructura de Datos JSON

### Licitaciones Normales
```json
{
  "metadata": {
    "tipo": "licitaciones_normales",
    "total_procesos": 25,
    "inversion_total": 121700000,
    "moneda": "Lempiras (L.)",
    "fecha_actualizacion": "2026-08-21",
    "estado": "vigentes",
    "cobertura": "Honduras",
    "fuente": "SICC Honduras Compras"
  },
  "procesos": [
    {
      "nro": 1,
      "expediente": "LPN-UNAH-A-001-2026",
      "descripcion": "Remodelación aulas",
      "institucion": "UNAH",
      "monto": 4200000,
      "cierre": "2026-08-12",
      "contacto": "unah-compras@unah.edu.hn",
      "link": "http://sicc.honducompras.gob.hn/...",
      "dias_para_cierre": 7,
      "tipo_licitacion": "licitacion_normal",
      "estado_proceso": "vigente",
      "fecha_extraccion": "2026-08-21"
    }
  ]
}
```

### Compras Menores
Estructura similar pero con:
- Rango de monto: L. 75,000 - L. 250,000
- `tipo_licitacion`: "compra_menor"

---

## 🔄 Flujos de Trabajo

### Actualización Manual
```bash
# Opción 1: Ejecutar script principal
bash scripts/actualizar.sh

# Opción 2: Pasos individuales
python3 scripts/extractor_honduras_compras.py
python3 scripts/generar_reportes.py
```

### Actualización Automática (Rutina Claude)
```bash
# Crear rutina diaria
/schedule

# Prompt:
# Regenerar reportes procesos construcción Honduras diariamente

# Configuración sugerida:
# - Intervalo: 0 23 * * * (5:00 PM Honduras = 11:00 PM UTC)
# - Modelo: claude-sonnet-5
```

---

## 📈 Estadísticas Esperadas

### Licitaciones Normales
- **Procesos**: 20-30
- **Inversión Total**: L. 100M - L. 150M
- **Instituciones**: UNAH, SIT, UNA, SEDENA, IHT, Municipalidades
- **Monto Promedio**: L. 4M - L. 6M

### Compras Menores
- **Procesos**: 25-35
- **Inversión Total**: L. 3M - L. 5M
- **Instituciones**: Todas
- **Monto Promedio**: L. 120K - L. 180K

---

## 🔗 Instituciones y Contactos

```
Universidades:
- UNAH: unah-compras@unah.edu.hn
- UNA: compras@una.hn
- UNACIFOR: compras@unacifor.hn

Entidades Públicas:
- SIT: licitaciones@sit.gob.hn
- SEDENA: compras@sedena.mil.hn
- SESEGU: compras@sesegu.gob.hn
- IHT: compras@iht.hn

Municipalidades:
- Tegucigalpa: compras@tegucigalpa.gob.hn
- San Pedro Sula: compras@sanpedrosula.gob.hn
- La Ceiba: compras@laceiba.gob.hn
- Danlí: compras@danli.gob.hn
- Y más...
```

---

## 🐛 Solución de Problemas

### Error: "SICC no disponible"
```
Causa: Servidor Honduras Compras no responde
Solución:
1. Verificar conexión a internet
2. Esperar y reintentar
3. Usar datos de plantilla (se genera automáticamente)
```

### Error: "ModuleNotFoundError: No module named 'requests'"
```
Solución:
pip install requests beautifulsoup4
```

### Reportes HTML no se generan
```
Verificar:
1. Archivos JSON existen en data/
2. Directorio reportes/ tiene permisos de escritura
3. Python 3.7+ está instalado
```

---

## 📝 Ejemplos de Uso

### Extraer y ver reportes
```bash
# Ejecutar actualización completa
bash scripts/actualizar.sh

# Abrir reportes en navegador (macOS)
open reportes/licitaciones.html
open reportes/compras-menores.html

# Abrir reportes en navegador (Linux)
xdg-open reportes/licitaciones.html
xdg-open reportes/compras-menores.html

# Abrir reportes en navegador (Windows)
start reportes/licitaciones.html
start reportes/compras-menores.html
```

### Consultar datos JSON
```bash
# Ver todos los procesos de licitación
cat data/licitaciones.json | python3 -m json.tool

# Ver solo procesos de UNAH
cat data/licitaciones.json | python3 -c "import sys, json; d=json.load(sys.stdin); [print(p) for p in d['procesos'] if p['institucion']=='UNAH']"

# Contar total de procesos
cat data/licitaciones.json | python3 -c "import sys, json; print(len(json.load(sys.stdin)['procesos']))"
```

---

## 🔄 Actualización Programada

### Opción 1: Cron (Linux/macOS)
```bash
# Editar crontab
crontab -e

# Agregar línea (cada día a las 5:00 PM Honduras)
0 23 * * * cd /ruta/procesos-construccion-honduras && bash scripts/actualizar.sh >> logs/actualizar.log 2>&1
```

### Opción 2: Claude Routine
```bash
/schedule

Prompt: Regenerar reportes procesos construcción Honduras
Cron: 0 23 * * * (5:00 PM Honduras)
Modelo: claude-sonnet-5
```

### Opción 3: GitHub Actions
Ver `.github/workflows/` para CI/CD automático

---

## 📊 Campos Disponibles por Proceso

| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|-------------|
| nro | int | 1 | Número de orden |
| expediente | string | LPN-UNAH-A-001-2026 | ID único del proceso |
| descripcion | string | Remodelación aulas | Descripción del proyecto |
| institucion | string | UNAH | Institución solicitante |
| monto | float | 4200000 | Monto en Lempiras |
| cierre | string | 2026-08-12 | Fecha de cierre (YYYY-MM-DD) |
| contacto | string | email@inst.hn | Correo de contacto |
| link | string | http://sicc... | Link al proceso en SICC |
| dias_para_cierre | int | 7 | Días faltantes para cierre |
| tipo_licitacion | string | licitacion_normal | Tipo de proceso |
| estado_proceso | string | vigente | vigente/cerrada/adjudicada |
| departamento | string | Francisco Morazán | Ubicación |
| tipo_proyecto | string | construccion | Categoría del trabajo |

---

## ✅ Checklist de Actualización

- [ ] Verificar conexión a internet
- [ ] Ejecutar `bash scripts/actualizar.sh`
- [ ] Verificar archivos JSON en `data/`
- [ ] Abrir reportes HTML en navegador
- [ ] Probar filtros y búsqueda
- [ ] Verificar números de instituciones
- [ ] Confirmar montos y fechas
- [ ] Sincronizar con Git
- [ ] Compartir links con equipo

---

## 📞 Soporte

Para reportar problemas o sugerencias:
1. Revisar este documento
2. Verificar logs en caso de errores
3. Contactar al equipo de desarrollo

---

**Versión**: 2.0  
**Última actualización**: 2026-08-21  
**Licencia**: CC BY 4.0
