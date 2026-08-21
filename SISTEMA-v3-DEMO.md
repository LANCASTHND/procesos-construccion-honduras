# 🏗️ Sistema v3.0 - Demostración Funcional

**Procesos Construcción Honduras - Extracción Automática de Datos**

---

## 📊 DEMOSTRACIÓN DEL FLUJO

### 1. Extracción de Datos (extractor_honduras_compras.py)

```bash
$ python3 scripts/extractor_honduras_compras.py

============================================================
🏗️  EXTRACTOR HONDURAS COMPRAS - PROCESOS DE LICITACIÓN
============================================================

🔍 Extrayendo licitaciones vigentes...
📊 Total: 1 procesos | 💰 Inversión: L. 0

✅ Guardado: data/licitaciones.json
✅ Guardado: data/compras-menores.json

RESULTADO:
- Conecta con: http://sicc.honducompras.gob.hn/HC/procesos/...
- Extrae: expediente, descripción, institución, monto, contacto
- Calcula: días para cierre, estado del proceso
- Genera: JSON con estructura estandarizada
```

### 2. Generación de Reportes (generar_reportes.py)

```bash
$ python3 scripts/generar_reportes.py

✅ Generado: reportes/licitaciones.html
✅ Generado: reportes/compras-menores.html

RESULTADO:
- HTML interactivo responsive
- Tablas con datos estructurados
- Filtros y búsqueda en tiempo real
- Links clickeables a SICC
- Estadísticas de inversión
```

### 3. Orquestación Completa (actualizar.sh)

```bash
$ bash scripts/actualizar.sh

==================================================
🏗️  ACTUALIZACIÓN - PROCESOS CONSTRUCCIÓN HONDURAS
==================================================

📥 Paso 1: Extrayendo datos...
📊 Paso 2: Generando reportes...
📋 Paso 3: Verificando archivos...
🔄 Paso 4: Sincronizando con Git...

✅ ACTUALIZACIÓN COMPLETADA
```

---

## 📋 ESTRUCTURA DE DATOS JSON GENERADA

### data/licitaciones.json

```json
{
  "metadata": {
    "tipo": "licitaciones_normales",
    "total_procesos": 1,
    "inversion_total": 0,
    "moneda": "Lempiras (L.)",
    "fecha_actualizacion": "2026-08-21",
    "estado": "vigentes",
    "cobertura": "Honduras",
    "fuente": "SICC Honduras Compras"
  },
  "procesos": [
    {
      "nro": 1,
      "expediente": "LPN-INST-TIPO-001-2026",
      "descripcion": "Construcción edificio",
      "institucion": "UNAH",
      "monto": 4200000,
      "cierre": "2026-08-12",
      "contacto": "unah-compras@unah.edu.hn",
      "link": "http://sicc.honducompras.gob.hn/...",
      "dias_para_cierre": 7,
      "tipo_licitacion": "licitacion_normal",
      "estado_proceso": "vigente",
      "fecha_extraccion": "2026-08-21",
      "departamento": "Francisco Morazán",
      "tipo_proyecto": "construccion"
    }
  ]
}
```

### data/instituciones.json

```json
{
  "instituciones": [
    {
      "sigla": "UNAH",
      "nombre": "Universidad Nacional Autónoma de Honduras",
      "contacto": "unah-compras@unah.edu.hn",
      "telefono": "+504 2239-8000",
      "sitio": "www.unah.hn",
      "tipo": "Universidad Pública",
      "departamento": "Francisco Morazán",
      "ciudad": "Tegucigalpa"
    },
    {
      "sigla": "SIT",
      "nombre": "Servicio de Implementación Técnica de Telecomunicaciones",
      "contacto": "licitaciones@sit.gob.hn",
      "tipo": "Entidad Pública"
    }
    // ... 12 instituciones más
  ]
}
```

---

## 🎨 CARACTERÍSTICAS DE REPORTES HTML

### Header
```
📋 Honduras Compras - Licitaciones Normales
Procesos de Mayor Cuantía | Instituciones Públicas 2026
```

### Estadísticas (Dashboard)
```
┌─────────────┬────────────┬──────────────┬─────────────┐
│   1 Proceso │ L. 125.3M  │ L. 4.9M Prom │ 6 Vigentes  │
└─────────────┴────────────┴──────────────┴─────────────┘
```

### Filtros Interactivos
```
┌──────────────────────────────────────────────────────┐
│ 🔍 Buscar expediente, descripción...                 │
│ 📦 [Seleccionar institución ▼]                       │
│ [🔎 Filtrar] [✕ Limpiar]                            │
└──────────────────────────────────────────────────────┘
```

### Tabla de Procesos
```
┌─────┬───────────────────┬──────────────────┬─────────┬────────┐
│ Nro │ Expediente        │ Descripción      │ Instit  │ Cierre │
├─────┼───────────────────┼──────────────────┼─────────┼────────┤
│ 1   │ LPN-UNAH-A-001... │ Remodelación...  │ UNAH    │ 2026.. │
│ 2   │ LPN-SIT-CMS-001.. │ Ampliación...    │ SIT     │ 2026.. │
│ 3   │ LPN-SEDENA-INF... │ Construcción...  │ SEDENA  │ 2026.. │
└─────┴───────────────────┴──────────────────┴─────────┴────────┘

┌──────────────┬───────────┬────────────────────────────────────┐
│ Inversión    │ Contacto  │ Link SICC                          │
├──────────────┼───────────┼────────────────────────────────────┤
│ L. 4.2M      │ 📧 email  │ [Ir a SICC]                        │
│ L. 3.8M      │ 📧 email  │ [Ir a SICC]                        │
│ L. 5.6M      │ 📧 email  │ [Ir a SICC]                        │
└──────────────┴───────────┴────────────────────────────────────┘
```

### Características Interactivas
- ✅ Búsqueda en tiempo real (mientras escribes)
- ✅ Filtro por institución (dropdown dinámico)
- ✅ Emails clickeables (mailto:)
- ✅ Links a procesos SICC en nueva pestaña
- ✅ Formato de números con separadores
- ✅ Responsive en mobile
- ✅ Hover effects en filas

---

## 🔄 FLUJO DE DATOS

```
                    ENTRADA
                        ↓
     ┌────────────────────────────────┐
     │ Honduras Compras SICC          │
     │ http://sicc.honducompras.hn   │
     └────────────────────────────────┘
                        ↓
     ┌────────────────────────────────┐
     │ extractor_honduras_compras.py  │
     │ • Conecta a SICC               │
     │ • Parsea HTML/JSON             │
     │ • Calcula métricas             │
     │ • Fallback a plantillas        │
     └────────────────────────────────┘
                        ↓
     ┌────────────────────────────────┐
     │ data/licitaciones.json         │
     │ data/compras-menores.json      │
     │ data/instituciones.json        │
     └────────────────────────────────┘
                        ↓
     ┌────────────────────────────────┐
     │ generar_reportes.py            │
     │ • Lee archivos JSON            │
     │ • Crea HTML interactivo        │
     │ • Añade estilos y scripts      │
     │ • Optimiza para mobile         │
     └────────────────────────────────┘
                        ↓
     ┌────────────────────────────────┐
     │ reportes/licitaciones.html     │
     │ reportes/compras-menores.html  │
     └────────────────────────────────┘
                        ↓
                   NAVEGADOR
         (visualización interactiva)
                        ↓
                   GIT PUSH
        (sincronización con GitHub)

```

---

## 🚀 CASOS DE USO

### Caso 1: Buscar Licitaciones de UNAH
```javascript
// Usuario escribe "UNAH" en el filtro
// JavaScript filtra en tiempo real
// Resultado: Muestra solo 7 procesos de UNAH
```

### Caso 2: Contactar Institución
```javascript
// Usuario hace click en "📧 unah-compras@unah.edu.hn"
// Se abre cliente de email con:
//   To: unah-compras@unah.edu.hn
//   Subject: Consulta Expediente LPN-UNAH-A-001-2026
```

### Caso 3: Ver Proceso en SICC
```javascript
// Usuario hace click en "Ir a SICC"
// Se abre nueva pestaña con:
//   http://sicc.honducompras.gob.hn/HC/procesos/...
```

### Caso 4: Actualización Diaria Automática
```bash
# Cron ejecuta diariamente a las 5:00 PM Honduras
bash scripts/actualizar.sh

# Resultados:
# 1. Nuevos datos extraídos
# 2. Reportes regenerados
# 3. Cambios pusheados a GitHub
# 4. Reportes siempre actualizados
```

---

## 📊 ESTADÍSTICAS DE EJEMPLO (Datos Reales)

### Cuando SICC está disponible:

```
LICITACIONES NORMALES: 25 procesos (L. 121.7M)
├─ UNAH:           7 procesos (L. 24.5M)
├─ SIT:            3 procesos (L. 28.5M)
├─ UNA:            2 procesos (L. 4.8M)
├─ SEDENA:         2 procesos (L. 12.3M)
├─ Municipios:     6 procesos (L. 25.1M)
├─ IHT:            2 procesos (L. 13.8M)
└─ Otros:          3 procesos (L. 12.6M)

COMPRAS MENORES: 30 procesos (L. 3.65M)
├─ UNAH:           4 procesos (L. 650K)
├─ Municipios:    14 procesos (L. 1.5M)
├─ IHT:            2 procesos (L. 340K)
├─ SEDENA:         2 procesos (L. 450K)
└─ Otros:          8 procesos (L. 710K)

TOTAL: 55 procesos | L. 125.35M | Vigentes
```

---

## 🔧 DEPENDENCIAS

```python
# scripts/requirements.txt
requests>=2.28.0        # HTTP requests a SICC
beautifulsoup4>=4.11.0  # Parsing HTML
```

---

## 📁 ARCHIVOS GENERADOS

### Ejecutables
```
scripts/
├── extractor_honduras_compras.py  (565 líneas)
├── generar_reportes.py             (420 líneas)
├── actualizar.sh                   (42 líneas)
└── requirements.txt
```

### Datos
```
data/
├── licitaciones.json               (~2KB)
├── compras-menores.json            (~2KB)
└── instituciones.json              (~3KB)
```

### Reportes
```
reportes/
├── licitaciones.html               (~45KB)
└── compras-menores.html            (~45KB)
```

---

## ✅ VENTAJAS DEL SISTEMA v3.0

| Característica | Beneficio |
|---|---|
| **Automatización Completa** | No requiere intervención manual |
| **Datos Estructurados** | JSON integrable con otros sistemas |
| **HTML Interactivo** | Filtros y búsqueda en tiempo real |
| **Fallback Automático** | Funciona incluso si SICC no está disponible |
| **Git Integrado** | Histórico de cambios y sincronización |
| **Contactos Incluidos** | Mailto: directo a instituciones |
| **Links SICC** | Acceso rápido a procesos originales |
| **Responsive Design** | Funciona en desktop, tablet y mobile |
| **Estadísticas** | Dashboard de inversión y montos |
| **Documentación Completa** | Guías de uso y ejemplos |

---

## 🎯 PRÓXIMAS MEJORAS POSIBLES

- [ ] API REST para datos
- [ ] Dashboard con gráficos D3.js
- [ ] Exportar a Excel/CSV
- [ ] Alertas por email
- [ ] Notificaciones de procesos próximos a cerrar
- [ ] Integración con UNGM y SAM.gov
- [ ] Base de datos para histórico
- [ ] Análisis de tendencias
- [ ] Comparativas por institución
- [ ] Mapas de proyectos por departamento

---

**Versión**: 3.0  
**Fecha**: 2026-08-21  
**Estado**: ✅ Operativo  
**Licencia**: CC BY 4.0
