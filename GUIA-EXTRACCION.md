# 🔄 Guía de Extracción de Datos - Honduras Procurement System

## Resumen Rápido

El sistema soporta **dos modos de extracción**:

1. **🤖 Automática** - Se ejecuta cada día a las 5:00 PM Honduras (11 PM UTC)
2. **🖱️ Manual/On-Demand** - Se ejecuta cuando lo solicitas

---

## 📊 Modo Automático (GitHub Actions)

### Horario
- **Hora Honduras:** 5:00 PM (17:00)
- **Hora UTC:** 11:00 PM (23:00)
- **Frecuencia:** Diariamente

### Características
- ✅ Se ejecuta automáticamente sin intervención
- ✅ Extrae datos de SICC
- ✅ Genera reportes HTML
- ✅ Sincroniza con Git automáticamente
- ✅ Historial completo disponible

### Monitoreo
Ver estado en GitHub Actions:
```
https://github.com/LANCASTHND/procesos-construccion-honduras/actions
```

---

## 🖱️ Modo Manual (On-Demand)

### Uso Básico

**Opción 1: Extracción Completa (Recomendado)**
```bash
bash scripts/actualizar.sh 1
```
Esto:
1. Extrae datos de SICC
2. Genera reportes HTML
3. Sincroniza con Git

**Opción 2: Solo Extracción**
```bash
bash scripts/actualizar.sh 2
```
Obtén datos sin generar reportes

**Opción 3: Solo Reportes**
```bash
bash scripts/actualizar.sh 3
```
Regenera reportes de datos existentes

**Opción 4: Verificar Estado**
```bash
bash scripts/actualizar.sh 4
```
Ve el estado actual del sistema

**Opción 5: Ver Historial**
```bash
bash scripts/actualizar.sh 5
```
Últimas 10 actualizaciones

### Modo Interactivo
```bash
bash scripts/actualizar.sh
```
Se mostrará un menú interactivo para seleccionar la opción

---

## 📋 Tabla de Opciones

| Opción | Nombre | Comando | Función |
|--------|--------|---------|---------|
| **1** | Completa | `bash scripts/actualizar.sh 1` | Extrae + Reportes + Git |
| **2** | Solo Datos | `bash scripts/actualizar.sh 2` | Solo extracción |
| **3** | Solo Reportes | `bash scripts/actualizar.sh 3` | Regenera HTML |
| **4** | Estado | `bash scripts/actualizar.sh 4` | Verifica sistema |
| **5** | Historial | `bash scripts/actualizar.sh 5` | Últimas actualizaciones |

---

## 🔍 Qué Ocurre en Cada Extracción

### Fase 1: Extracción de Datos
```
1. Conecta a SICC Honduras Compras
2. Selecciona filtros (Obras, Licitaciones, Compras Menores)
3. Busca procesos vigentes
4. Extrae información de cada proceso:
   - Expediente
   - Modalidad
   - Etapa (Recepción de ofertas, etc)
   - Fechas de inicio
   - Calcula días para cierre
5. Guarda en JSON
```

**Salida esperada:**
```
data/licitaciones.json        (30 procesos)
data/compras-menores.json     (30 procesos)
```

### Fase 2: Generación de Reportes
```
1. Lee archivos JSON
2. Genera tablas HTML interactivas
3. Añade filtros de búsqueda
4. Crea reportes styled
```

**Salida esperada:**
```
reportes/licitaciones.html     (tabla con 30 procesos)
reportes/compras-menores.html  (tabla con 30 procesos)
```

### Fase 3: Sincronización Git
```
1. Añade archivos modificados
2. Crea commit con timestamp
3. Empuja a rama principal
4. Actualiza historial
```

**Estado esperado:**
```
✅ Cambios sincronizados con GitHub
✅ Historial disponible
```

---

## 📊 Datos Extraídos

### Estructura JSON
Cada proceso contiene:
```json
{
  "expediente": "LPN No. 08-2026-SEAPI-UNAH",
  "descripcion": "Licitación pública nacional",
  "etapa": "Recepción de Ofertas",
  "modalidad": "Licitación pública nacional",
  "fecha_inicio": "17/08/2026",
  "cierre": "21/09/2026",
  "dias_para_cierre": 24,
  "estado_proceso": "vigente",
  "tipo_licitacion": "licitacion"
}
```

### Metadatos
```json
{
  "metadata": {
    "total_procesos": 30,
    "fecha_actualizacion": "2026-08-27 05:34:00",
    "estado": "vigentes",
    "fuente": "SICC Honduras Compras",
    "metodo_extraccion": "playwright-navegador-automatizado-javascript"
  }
}
```

---

## 🔧 Requisitos Previos

### Dependencias Python
```bash
pip install -r scripts/requirements.txt
```

Instala:
- `playwright` - Navegador automatizado
- `beautifulsoup4` - Parsing HTML
- `requests` - HTTP requests

### Dependencias del Sistema
- Python 3.7+
- Bash (Linux/macOS) o PowerShell (Windows)
- Git (para sincronización)

---

## 📝 Ejemplos de Uso

### Escenario 1: Actualización Diaria Manual
```bash
# Cada mañana, actualizar datos manualmente
bash scripts/actualizar.sh 1
```

### Escenario 2: Verificar antes de Compartir
```bash
# Verifica estado antes de compartir reportes
bash scripts/actualizar.sh 4
```

### Escenario 3: Solo Actualizar Reportes
```bash
# Si los datos son correctos, solo regenera HTML
bash scripts/actualizar.sh 3
```

### Escenario 4: Debugging
```bash
# Ver qué cambios hubo
bash scripts/actualizar.sh 5
```

---

## 📈 Monitoreo de Ejecuciones

### Ver estado actual
```bash
bash scripts/actualizar.sh 4
```

Muestra:
- ✅ Archivos disponibles
- 📊 Cantidad de procesos
- 🌿 Rama Git actual
- 📋 Últimas 3 actualizaciones

### Ver historial completo
```bash
git log --oneline -- data/ reportes/
```

### Ver cambios específicos
```bash
git diff HEAD~1 HEAD -- data/licitaciones.json
```

---

## ⏰ Automatización Diaria

### GitHub Actions
El sistema se ejecuta automáticamente cada día sin intervención manual.

**Archivo de configuración:**
```
.github/workflows/daily-update.yml
```

**Cronograma:**
```
0 23 * * *  (11 PM UTC / 5 PM Honduras)
```

### Verificar ejecuciones automáticas
```
https://github.com/LANCASTHND/procesos-construccion-honduras/actions
```

---

## 🐛 Troubleshooting

### Problema: SICC no responde
**Solución:**
- Verificar conexión a internet
- Esperar 5 minutos y reintentar
- SICC puede estar en mantenimiento

### Problema: Python no encuentra módulos
**Solución:**
```bash
pip install -r scripts/requirements.txt --upgrade
```

### Problema: Git push falla
**Solución:**
```bash
# Verificar estado
git status

# Actualizar rama local
git fetch origin
git pull origin claude/honduras-procurement-report-hv200y

# Reintentar extracción
bash scripts/actualizar.sh 1
```

### Problema: Reportes están en blanco
**Solución:**
- Verificar que data/*.json exista y tenga datos
- Regenerar reportes: `bash scripts/actualizar.sh 3`

---

## 📞 Contacto y Soporte

Para problemas técnicos o preguntas:

📧 **Email:** gerencia@lancast.biz
🌐 **GitHub:** https://github.com/LANCASTHND/procesos-construccion-honduras

---

## 📚 Archivos Relacionados

- `scripts/extractor_honduras_compras_v3.py` - Extractor de datos
- `scripts/generar_reportes.py` - Generador de reportes
- `.github/workflows/daily-update.yml` - Automatización GitHub Actions
- `data/licitaciones.json` - Datos extraídos (licitaciones)
- `data/compras-menores.json` - Datos extraídos (compras menores)
- `reportes/licitaciones.html` - Reporte HTML (licitaciones)
- `reportes/compras-menores.html` - Reporte HTML (compras menores)

---

**Versión:** 3.0  
**Última actualización:** 27 de agosto de 2026  
**Estado:** ✅ Operativo
