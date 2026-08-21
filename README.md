# 🏗️ Honduras Procesos de Construcción 2026

Sistema integral de reportes de **licitaciones** y **compras menores** para procesos de construcción y remodelación en Honduras.

## 📊 Datos Consolidados

| Tipo | Procesos | Inversión | Estado |
|------|----------|-----------|--------|
| 📋 **Licitaciones Normales** | 25 | L. 121.7M | Vigentes |
| ⚡ **Compras Menores** | 30 | L. 3.65M | Vigentes |
| **TOTAL** | **55** | **L. 125.35M** | ✅ Activo |

## 🔗 Acceso Rápido a Reportes

### Reportes Interactivos en Línea
- **Licitaciones:** [https://claude.ai/code/artifact/9ecb6c99-21d1-4ae9-8d71-29485d085f41](https://claude.ai/code/artifact/9ecb6c99-21d1-4ae9-8d71-29485d085f41)
- **Compras Menores:** [https://claude.ai/code/artifact/aaf4da24-5210-40be-82e8-8d07e824bd0a](https://claude.ai/code/artifact/aaf4da24-5210-40be-82e8-8d07e824bd0a)

### Generar Localmente
```bash
# Clonar repositorio
git clone https://github.com/[tu-usuario]/honduras-construccion-procesos.git
cd honduras-construccion-procesos

# Abrir reportes
open reportes/licitaciones.html
open reportes/compras-menores.html
```

## 🏛️ Instituciones Incluidas

### Universidades (9 procesos)
- ✅ UNAH - Universidad Nacional Autónoma de Honduras
- ✅ UNA - Universidad Nacional de Agricultura
- ✅ UNACIFOR - Universidad Nacional de Ciencias Forestales

### Entidades Públicas (5 procesos)
- ✅ SIT - Secretaría de Infraestructura y Transporte
- ✅ SEDENA - Secretaría de Defensa Nacional
- ✅ SESEGU - Secretaría de Seguridad Pública

### Turismo (4 procesos)
- ✅ IHT - Instituto Hondureño de Turismo

### Municipalidades (7 jurisdicciones, 14 procesos)
- ✅ Tegucigalpa
- ✅ San Pedro Sula
- ✅ La Ceiba
- ✅ Danlí
- ✅ El Rama
- ✅ Comayagua
- ✅ Choloma

## 📂 Estructura del Repositorio

```
honduras-construccion-procesos/
├── README.md
├── LICENSE (CC BY 4.0)
├── .gitignore
│
├── data/
│   ├── licitaciones.json          # Datos de 25 licitaciones
│   ├── compras-menores.json       # Datos de 30 compras menores
│   ├── licitaciones.csv           # Export CSV
│   └── compras-menores.csv        # Export CSV
│
├── reportes/
│   ├── licitaciones.html          # Tabla interactiva licitaciones
│   ├── compras-menores.html       # Tabla interactiva compras
│   └── index.html                 # Página principal
│
├── scripts/
│   ├── generar-reportes.ps1       # Script PowerShell para generar
│   ├── actualizar-datos.ps1       # Script para actualizar datos
│   └── sync-github.sh             # Script para sincronizar
│
├── docs/
│   ├── RESUMEN-COMPLETO.md        # Resumen ejecutivo
│   ├── GUIA-USO.md                # Guía de uso
│   ├── CONTACTOS.md               # Contactos institucionales
│   └── METODOLOGIA.md             # Metodología de recopilación
│
└── .github/
    └── workflows/
        └── update-reportes.yml    # GitHub Actions (actualización diaria)
```

## 🚀 Inicio Rápido

### 1. Ver reportes en línea
Accede directamente a los links de Claude (arriba)

### 2. Descargar datos
```bash
# Descargar JSON
curl -O https://raw.githubusercontent.com/[tu-usuario]/honduras-construccion-procesos/main/data/licitaciones.json

# Descargar CSV
curl -O https://raw.githubusercontent.com/[tu-usuario]/honduras-construccion-procesos/main/data/licitaciones.csv
```

### 3. Usar en tu aplicación
```python
import json

# Cargar datos
with open('data/licitaciones.json') as f:
    licitaciones = json.load(f)

# Filtrar por institución
unah_procesos = [p for p in licitaciones if p['institución'] == 'UNAH']
print(f"UNAH tiene {len(unah_procesos)} procesos")
```

## 📋 Características de los Reportes

### Tablas Interactivas
✅ Filtro por institución  
✅ Búsqueda por expediente  
✅ Rango de inversión  
✅ Contactos email directos  
✅ Exportar a Excel  
✅ Responsive (móvil/tablet/desktop)  

### Datos Incluidos
✅ Número de expediente completo  
✅ Descripción del proyecto  
✅ Institución responsable  
✅ Fecha de cierre  
✅ Inversión en Lempiras  
✅ Email de contacto directo  

## 📊 Estadísticas por Institución

### Licitaciones Normales (25 procesos)
```
UNAH:          7 procesos | L. 24.5M
SIT:           3 procesos | L. 28.5M
UNA:           2 procesos | L. 4.8M
SEDENA:        2 procesos | L. 12.3M
Municipios:    6 procesos | L. 25.1M
IHT:           2 procesos | L. 13.8M
Otros:         3 procesos | L. 12.6M
```

### Compras Menores (30 procesos)
```
UNAH:          4 procesos | L. 650K
Municipios:   14 procesos | L. 1.5M
IHT:           2 procesos | L. 340K
SEDENA:        2 procesos | L. 450K
Otros:         8 procesos | L. 710K
```

## 🔄 Actualización de Datos

Los datos se actualizan:
- ✅ Manualmente cuando hay cambios
- ✅ Automáticamente cada día a las 5:00 PM Honduras (via GitHub Actions)
- ✅ En tiempo real en los reportes interactivos

## 📧 Contactos Principales

Todos los contactos están incluidos en las tablas interactivas.

**Para participar en procesos:**
1. Abre el reporte correspondiente
2. Identifica el proceso que te interesa
3. Haz clic en el email de contacto
4. Envía tu interés directamente a la institución

## 📄 Licencia

Este proyecto está bajo licencia **Creative Commons Attribution 4.0 (CC BY 4.0)**

- ✅ Puedes usar, modificar y distribuir
- ✅ Debes dar crédito
- ✅ Permitido uso comercial

## 🤝 Contribuir

¿Encontraste datos faltantes o errores?

1. Abre un Issue describiendo el cambio
2. Proporciona fuente/referencia
3. Incluye datos actualizados

## 📞 Soporte

- 📧 Issues: GitHub Issues en este repositorio
- 📋 Reportes: Ver carpeta `/reportes`
- 📚 Documentación: Ver carpeta `/docs`

## 🗺️ Roadmap

- [ ] Agregar procesos de departamentos adicionales
- [ ] Integración con API de Hondumpras
- [ ] Dashboard de análisis
- [ ] Exportación a Excel avanzada
- [ ] Notificaciones de nuevos procesos
- [ ] Búsqueda por palabras clave

## 📈 Estadísticas del Proyecto

- **Procesos monitoreos:** 55
- **Instituciones:** 14
- **Municipalidades:** 7 de 298
- **Cobertura inversión:** L. 125.35M
- **Última actualización:** 2026-08-08

---

**Versión:** 2.0  
**Última actualización:** 2026-08-08  
**Estado:** ✅ Completo y Vigente

Para más información, consulta la carpeta `/docs`
