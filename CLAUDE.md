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
├── README.md                    # Documentación principal
├── LICENSE                      # CC BY 4.0
├── CLAUDE.md                    # Este archivo
├── RESUMEN-EJECUTIVO-FINAL.md   # Resumen completo
│
├── .claude/
│   └── launch.json              # Configuración Claude Code
│
├── data/
│   ├── licitaciones.json        # 25 procesos (L. 121.7M)
│   └── compras-menores.json     # 30 procesos (L. 3.65M)
│
├── reportes/
│   ├── licitaciones.html        # Tabla interactiva
│   └── compras-menores.html     # Tabla interactiva
│
├── scripts/
│   └── actualizar-diario.ps1    # Script de actualización
│
└── docs/
    └── SETUP-GITHUB.md          # Guía de configuración
```

---

## 🚀 TAREAS COMUNES

### 1. Generar Reportes Actualizados

```bash
# Desde Claude Code
/run Procesos Construccion Honduras

# Resultado: Actualiza datos y sube a GitHub
```

### 2. Visualizar Licitaciones

```bash
# Opción A: Abrir archivo local
/run Abrir Licitaciones HTML

# Opción B: Ver en línea
# https://claude.ai/code/artifact/9ecb6c99-21d1-4ae9-8d71-29485d085f41
```

### 3. Visualizar Compras Menores

```bash
# Opción A: Abrir archivo local
/run Abrir Compras Menores HTML

# Opción B: Ver en línea
# https://claude.ai/code/artifact/aaf4da24-5210-40be-82e8-8d07e824bd0a
```

### 4. Acceder a Datos JSON

```bash
# Licitaciones
cat data/licitaciones.json

# Compras Menores
cat data/compras-menores.json
```

### 5. Verificar Estado de Git

```bash
git status
git log --oneline
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

## ⏰ ACTUALIZACIÓN AUTOMÁTICA

### Opción 1: Rutina con Claude (/schedule)

```
/schedule

Prompt: Regenerar reportes procesos construcción Honduras
Cron: 0 23 * * * (5:00 PM Honduras)
Modelo: claude-sonnet-5
```

### Opción 2: Rutina Local (Task Scheduler)

```powershell
# Crear tarea: Ejecutar actualizar-diario.ps1
# Cada día a las 5:00 PM Honduras (11:00 PM UTC)
```

---

## 💡 TIPS

- **Reportes HTML:** Abren en navegador con filtros interactivos
- **Datos JSON:** Para integrar en otros sistemas
- **GitHub:** Sincronización automática con `/run`
- **Contactos:** Click en email para contactar directamente

---

## 📚 DOCUMENTACIÓN ADICIONAL

- `README.md` - Información completa
- `RESUMEN-EJECUTIVO-FINAL.md` - Resumen ejecutivo
- `docs/SETUP-GITHUB.md` - Guía de configuración
- `data/` - Archivos JSON con todos los datos

---

## ✅ CHECKLIST DE USO

- [ ] Clonar/Descargar repositorio
- [ ] Ejecutar reportes (`/run`)
- [ ] Visualizar en navegador o línea
- [ ] Configurar actualización automática
- [ ] Sincronizar cambios con GitHub

---

**Versión:** 2.0  
**Última actualización:** 2026-08-08  
**Estado:** ✅ Operativo  
**Licencia:** CC BY 4.0

---

## 🎯 PRÓXIMAS MEJORAS

- [ ] Agregar procesos de UNGM
- [ ] Integrar SAM.gov
- [ ] Dashboard consolidado
- [ ] Filtros avanzados
- [ ] Gráficos de inversión

**¿Dudas? Revisa README.md o RESUMEN-EJECUTIVO-FINAL.md**
