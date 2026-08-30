# 🔔 Monitoreo Automático de Procesos UNGM

Sistema de alertas que detecta automáticamente procesos **nuevos**, **modificados** o **removidos** en UNGM Honduras.

## 🚀 Inicio Rápido

### Paso 1: Guardar Estado Inicial

La primera vez que uses el monitor, debes extraer y guardar los procesos actuales:

```bash
# 1. Ir a UNGM y aplicar filtros:
#    - País: Honduras
#    - Tipo: Construction / Materials

# 2. Importar procesos
python3 scripts/importar_ungm_manual.py

# 3. Inicializar monitor (primera ejecución)
python3 scripts/monitor_ungm.py
```

Output esperado:
```
⚠️  Primera ejecución - Guardando como referencia
📊 Procesos guardados: 12
```

### Paso 2: Monitoreo Regular

Cada vez que actualices los procesos en UNGM:

```bash
# 1. Ir a UNGM, aplicar filtros y copiar procesos nuevos

# 2. Importar (actualiza data/ungm-honduras.json)
python3 scripts/importar_ungm_manual.py

# 3. Ejecutar monitor
python3 scripts/monitor_ungm.py
```

Output esperado:
```
🆕 PROCESOS NUEVOS (2)
  ✅ UNGM-2026-015
     Título: Supply of Steel Materials...
     
✏️  PROCESOS MODIFICADOS (0)

🗑️  PROCESOS REMOVIDOS (0)

📋 RESUMEN
  Total Nuevos: 2
  Total Modificados: 0
  Total Removidos: 0
```

## 🤖 Monitoreo Automático (RECOMENDADO)

Para que el sistema **chequee automáticamente** cada día:

```bash
# Crear rutina automática
/schedule

Nombre: Monitorear UNGM Honduras
Prompt: python3 scripts/monitor_ungm.py
Cron: 0 18 * * * (6:00 PM Honduras = 12:00 AM UTC+1 next day)
Modelo: claude-opus-5
```

Esto hará que:
- ✅ Se ejecute automáticamente cada día
- ✅ Detecte procesos nuevos
- ✅ Te notifique cuando hay cambios
- ✅ Guarde un registro en `logs/ungm-monitor.log`

## 📊 Cómo Funciona

```
Tu extracción manual en UNGM
         ↓
importar_ungm_manual.py (actualiza data/ungm-honduras.json)
         ↓
monitor_ungm.py (compara con estado anterior)
         ↓
Detecta: Nuevos, Modificados, Removidos
         ↓
Genera reporte y lo guarda en logs/ungm-monitor.log
         ↓
Actualiza histórico para próxima comparación
```

## 📋 Archivos Involucrados

| Archivo | Propósito |
|---------|-----------|
| `data/ungm-honduras.json` | Datos actuales de UNGM |
| `data/.ungm-historico.json` | Estado anterior (para comparación) |
| `logs/ungm-monitor.log` | Historial de cambios detectados |

## 🔄 Flujo Completo Recomendado

### Opción A: Manual Diario
```bash
# Cada mañana/tarde
1. Abrir UNGM → Aplicar filtros → Copiar tabla
2. python3 scripts/importar_ungm_manual.py
3. python3 scripts/monitor_ungm.py
4. Ver qué procesos son nuevos
5. python3 scripts/generar_reporte_ungm.py (opcional, si hay cambios)
```

### Opción B: Automático + Sincronización
```bash
# Configurar rutina de monitoreo automático
/schedule
# (Configura como se describe arriba)

# Cuando haya cambios detectados:
git add data/ungm-honduras.json reportes/ungm-construccion.html
git commit -m "Actualización automática de procesos UNGM"
git push
```

### Opción C: Híbrida (RECOMENDADA)
```bash
# 1. Rutina automática corre cada día
# 2. Tú sincronizas datos a GitHub cuando hay cambios importantes
# 3. Reportes se generan bajo demanda
```

## 📈 Ver Reportes

### Reporte en Terminal
```bash
python3 scripts/monitor_ungm.py
```
Muestra directamente en pantalla cambios recientes.

### Historial Completo
```bash
cat logs/ungm-monitor.log
```
Ver todos los cambios detectados desde el inicio.

### Reporte HTML (después de cambios)
```bash
python3 scripts/generar_reporte_ungm.py
open reportes/ungm-construccion.html
```

## 🔔 Recibir Alertas

### Opción 1: Email (Automático)
Si configuras rutina con `/schedule`, puedes recibir notificaciones por email.

### Opción 2: GitHub (Ver cambios en commits)
```bash
git log --oneline  # Ver cambios recientes
```

### Opción 3: Manual (Revisar logs)
```bash
tail -50 logs/ungm-monitor.log  # Últimos cambios
```

## ⚙️ Configuración Avanzada

### Cambiar Frecuencia de Chequeo

Si quieres que se chequee más frecuentemente:

```bash
# Dos veces al día (9 AM y 5 PM Honduras)
/schedule
Nombre: Monitorear UNGM (Mañana)
Cron: 0 14 * * *  # 9 AM Honduras

/schedule  
Nombre: Monitorear UNGM (Tarde)
Cron: 0 22 * * *  # 5 PM Honduras
```

### Personalizar Notificaciones

El monitor detecta:
- **Nuevos procesos** (sin fecha_cierre anterior)
- **Cambios de fechas** (fecha_cierre modificada)
- **Procesos removidos** (ya no aparecen en UNGM)

## ❓ Preguntas Frecuentes

**P: ¿Con qué frecuencia debo actualizar datos en UNGM?**  
R: Se recomienda 1-2 veces por semana. El monitor detectará cualquier cambio.

**P: ¿Qué pasa si no actualizo durante días?**  
R: El monitor solo ve cambios desde la última actualización. Seguirá trabajando normalmente.

**P: ¿Puedo recibir alertas automáticas?**  
R: Sí, configura rutina automática con `/schedule` y recibirás notificaciones.

**P: ¿Qué pasa si UNGM quita un proceso?**  
R: El monitor lo detectará como "PROCESO REMOVIDO" en el reporte.

## 📞 Contacto de Instituciones

Una vez detectes procesos nuevos, puedes contactar directamente a las instituciones. Ver:
```bash
cat data/instituciones.json
```

## 🔗 Links Útiles

- UNGM: https://www.ungm.org/Public/Notice
- Monitor script: `scripts/monitor_ungm.py`
- Importador: `scripts/importar_ungm_manual.py`
- Generador de reportes: `scripts/generar_reporte_ungm.py`

---

**Resumen:** El monitor es tu asistente que detecta lo nuevo. Tú solo necesitas:
1. Actualizar datos en UNGM cuando puedas
2. Ejecutar importador y monitor
3. El sistema te avisa de cambios automáticamente
