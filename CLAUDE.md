# 🏗️ Claude Code - Procesos Construcción Honduras

**Sistema de reportes interactivos para procesos de construcción en Honduras**

---

## ⚡ INICIO RÁPIDO CON CLAUDE CODE

### Desde Claude Code CLI:

```bash
claude code procesos-construccion-honduras
```

### Opciones de Ejecución:

1. **Ver Licitaciones:**
   ```bash
   /run Abrir Licitaciones HTML
   ```

2. **Ver Compras Menores:**
   ```bash
   /run Abrir Compras Menores HTML
   ```

3. **Actualizar Reportes:**
   ```bash
   /run Procesos Construccion Honduras
   ```

---

## 📊 INFORMACIÓN DEL PROYECTO

**Nombre:** Procesos de Construcción Honduras 2026  
**Tipo:** Sistema de Reportes Interactivos  
**Procesos:** 55 (25 licitaciones + 30 compras menores)  
**Inversión:** L. 125.35M  
**Instituciones:** 14 públicas + 7 municipalidades  
**Estado:** ✅ Operativo y Vigente

---

## 📋 ESTRUCTURA DE ARCHIVOS

```
procesos-construccion-honduras/
├── README.md                           # Documentación principal
├── LICENSE                             # CC BY 4.0
├── CLAUDE.md                           # Este archivo
├── RESUMEN-EJECUTIVO-FINAL.md          # Resumen completo
│
├── .claude/
│   └── launch.json                     # Configuración Claude Code
│
├── data/
│   ├── licitaciones.json               # Procesos licitación (actualizable)
│   ├── compras-menores.json            # Compras menores (actualizable)
│   └── instituciones.json              # Directorio de instituciones
│
├── reportes/
│   ├── licitaciones.html               # Tabla interactiva licitaciones
│   └── compras-menores.html            # Tabla interactiva compras menores
│
├── scripts/
│   ├── README.md                       # Documentación de scripts
│   ├── extractor_honduras_compras.py   # 🔄 Extrae datos de SICC
│   ├── generar_reportes.py             # 📊 Genera HTML desde JSON
│   ├── actualizar.sh                   # ⚙️  Orquestador completo
│   └── requirements.txt                # Dependencias Python
│
└── docs/
    └── SETUP-GITHUB.md                 # Guía de configuración
```

---

## 🚀 TAREAS COMUNES

### 1. Actualizar Reportes con Datos Reales

**Opción A: Script Completo (Recomendado)**
```bash
# Ejecuta: extracción + generación HTML + sincronización Git
bash scripts/actualizar.sh
```

**Opción B: Pasos Individuales**
```bash
# Instalar dependencias (primera vez)
pip install -r scripts/requirements.txt

# Extraer datos de Honduras Compras
python3 scripts/extractor_honduras_compras.py

# Generar reportes HTML
python3 scripts/generar_reportes.py
```

### 2. Visualizar Licitaciones

```bash
# Abrir archivo local en navegador
open reportes/licitaciones.html  # macOS
xdg-open reportes/licitaciones.html  # Linux
start reportes/licitaciones.html  # Windows
```

### 3. Visualizar Compras Menores

```bash
# Abrir archivo local en navegador
open reportes/compras-menores.html
```

### 4. Acceder a Datos JSON

```bash
# Ver todas licitaciones
cat data/licitaciones.json

# Ver todas compras menores
cat data/compras-menores.json

# Ver directorio de instituciones
cat data/instituciones.json
```

### 5. Verificar Estado de Git

```bash
git status
git log --oneline
git branch -a
```

---

## 📊 FILTROS DE BÚSQUEDA

**Los reportes incluyen filtros por:**
- ✅ Institución (UNAH, SIT, UNA, SEDENA, etc.)
- ✅ Rango de inversión (L. 75K - L. 12.5M)
- ✅ Búsqueda por expediente
- ✅ Buscar por descripción de proyecto

**Tipos de Proyectos Incluidos:**
- Construcción de infraestructura
- Remodelación de edificios
- Reparación de instalaciones
- Ampliación de estructuras
- Mantenimiento de infraestructura
- Pavimentación y drenaje

---

## 🔧 CONFIGURACIÓN RECOMENDADA

### En `.claude/settings.json` agregar:

```json
{
  "allowlist": [
    "Bash",
    "Read",
    "Edit",
    "Write",
    "Glob",
    "Grep"
  ]
}
```

### Hooks (Opcional):

```json
{
  "hooks": {
    "on-save": "git add -A && git commit -m 'Actualización automática' && git push origin master"
  }
}
```

---

## 📞 CONTACTOS POR INSTITUCIÓN

### Universidades
- **UNAH:** unah-compras@unah.edu.hn
- **UNA:** compras@una.hn
- **UNACIFOR:** compras@unacifor.hn

### Entidades Públicas
- **SIT:** licitaciones@sit.gob.hn
- **SEDENA:** compras@sedena.mil.hn
- **SESEGU:** compras@sesegu.gob.hn

### Turismo
- **IHT:** compras@iht.hn

### Municipalidades
- **Tegucigalpa:** compras@tegucigalpa.gob.hn
- **San Pedro Sula:** compras@sanpedrosula.gob.hn
- **La Ceiba:** compras@laceiba.gob.hn
- **Danlí:** compras@danli.gob.hn
- **El Rama:** compras@elrama.gob.hn
- **Comayagua:** compras@comayagua.gob.hn
- **Choloma:** compras@munichol.hn

---

## 🔗 LINKS PRINCIPALES

| Recurso | URL |
|---------|-----|
| **GitHub Repo** | https://github.com/LANCASTHND/procesos-construccion-honduras |
| **Licitaciones (Web)** | https://claude.ai/code/artifact/9ecb6c99-21d1-4ae9-8d71-29485d085f41 |
| **Compras Menores (Web)** | https://claude.ai/code/artifact/aaf4da24-5210-40be-82e8-8d07e824bd0a |
| **Datos JSON** | ./data/ |

---

## 📈 ESTADÍSTICAS

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

## 🔄 FLUJO DE ACTUALIZACIÓN DE DATOS

### Cómo Funciona el Sistema de Scripts

```
Honduras Compras SICC
        ↓
extractor_honduras_compras.py  (Extrae datos reales)
        ↓
data/licitaciones.json
data/compras-menores.json
        ↓
generar_reportes.py  (Crea HTML interactivo)
        ↓
reportes/licitaciones.html
reportes/compras-menores.html
        ↓
Git Push (Sincroniza cambios)
```

### Scripts Disponibles

| Script | Función | Uso |
|--------|---------|-----|
| `actualizar.sh` | Ejecuta flujo completo | `bash scripts/actualizar.sh` |
| `extractor_honduras_compras.py` | Extrae datos de SICC | `python3 scripts/extractor_honduras_compras.py` |
| `generar_reportes.py` | Crea HTML desde JSON | `python3 scripts/generar_reportes.py` |

**Ver documentación completa:** `scripts/README.md`

---

## ⏰ ACTUALIZACIÓN AUTOMÁTICA

### Opción 1: Rutina con Claude (/schedule) ⭐ RECOMENDADO

```
/schedule

Nombre: Actualizar procesos Honduras
Prompt: Ejecutar bash scripts/actualizar.sh
Cron: 0 23 * * * (5:00 PM Honduras = 11:00 PM UTC)
Modelo: claude-sonnet-5
```

### Opción 2: Cron Local (Linux/macOS)

```bash
# Editar crontab
crontab -e

# Agregar línea (cada día a las 11:00 PM UTC)
0 23 * * * cd /ruta/procesos-construccion-honduras && bash scripts/actualizar.sh >> logs/actualizar.log 2>&1
```

### Opción 3: Task Scheduler (Windows)

```powershell
# Crear tarea programada que ejecute:
# bash scripts/actualizar.sh
# Horario: 5:00 PM Honduras (11:00 PM UTC)
```

---

## 💡 TIPS Y CARACTERÍSTICAS

### Reportes Interactivos
- ✅ Búsqueda en tiempo real por expediente
- ✅ Filtro por institución
- ✅ Links clickeables a procesos SICC
- ✅ Contactos con mailto: integrado
- ✅ Estadísticas de inversión
- ✅ Responsive en mobile

### Datos en JSON
- ✅ Estructura estandarizada
- ✅ Metadata completa
- ✅ Integrable con otros sistemas
- ✅ Actualizable automáticamente

### Extracción de Datos
- ✅ Conexión a SICC Honduras Compras
- ✅ Extrae datos reales y vigentes
- ✅ Fallback a plantilla si SICC no disponible
- ✅ Calcula días para cierre
- ✅ Asocia contactos automáticamente

### Automatización
- ✅ Scripts Python/Bash modulares
- ✅ Actualización programada
- ✅ Sincronización con Git
- ✅ Logs de ejecución
- ✅ Manejo de errores

### Contacto Directo
- 📧 Click en email para enviar mensaje
- 📞 Teléfonos incluidos en instituciones.json
- 🌐 Links a sitios web institucionales

---

## 📚 DOCUMENTACIÓN ADICIONAL

| Archivo | Descripción |
|---------|-------------|
| `README.md` | Información general y estadísticas |
| `RESUMEN-EJECUTIVO-FINAL.md` | Resumen ejecutivo del proyecto |
| `scripts/README.md` | Documentación completa de scripts |
| `docs/SETUP-GITHUB.md` | Guía de configuración inicial |
| `data/instituciones.json` | Directorio completo de instituciones |

---

## ✅ CHECKLIST DE USO

- [ ] Clonar/Descargar repositorio
- [ ] Ejecutar reportes (`/run`)
- [ ] Visualizar en navegador o línea
- [ ] Configurar actualización automática
- [ ] Sincronizar cambios con GitHub

---

**Versión:** 3.0  
**Última actualización:** 2026-08-21  
**Estado:** ✅ Operativo con Extracción Automática  
**Licencia:** CC BY 4.0

---

## 🎯 CARACTERÍSTICAS v3.0 (NUEVO)

- ✅ Scripts Python para extracción automática de SICC
- ✅ Generador de reportes HTML mejorado
- ✅ Orquestador de flujo completo (actualizar.sh)
- ✅ Directorio de instituciones con contactos completos
- ✅ Soporte para filtros y búsqueda en tiempo real
- ✅ Sincronización automática con Git
- ✅ Manejo de errores y fallbacks

## 🔜 PRÓXIMAS MEJORAS

- [ ] Dashboard con gráficos de inversión
- [ ] Exportar a Excel/CSV
- [ ] Integración con email notifications
- [ ] API REST para datos
- [ ] Alertas de procesos próximos a cerrar
- [ ] Integración UNGM y SAM.gov

**¿Dudas? Revisa:**
- `README.md` - Visión general
- `scripts/README.md` - Documentación técnica
- `RESUMEN-EJECUTIVO-FINAL.md` - Resumen ejecutivo
