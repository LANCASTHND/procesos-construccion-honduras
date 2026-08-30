# 📊 Guía: Extraer Procesos de UNGM

## Problema Técnico

UNGM (https://www.ungm.org/Public/Notice) usa **JavaScript dinámico** para cargar datos. Esto significa:
- ✅ Los humanos pueden verlo en navegadores
- ✅ curl descarga la página, pero sin datos
- ❌ Bots automáticos no pueden ejecutar JavaScript en este ambiente

## Soluciones Disponibles

### ✅ Opción 1: Importar Manualmente (Recomendado)

**Paso 1:** Ir a UNGM y filtrar procesos
```
1. Abre: https://www.ungm.org/Public/Notice
2. Aplica filtros:
   - País: Honduras
   - Tipo: Construction / Materials (selecciona uno o ambos)
3. Copia los resultados (Ctrl+A en la tabla)
```

**Paso 2:** Usar el importador
```bash
# Modo interactivo (ingresa procesos uno a uno)
python3 scripts/importar_ungm_manual.py

# O desde archivo CSV
python3 scripts/importar_ungm_manual.py procesos.csv
```

### 📋 Formato CSV Esperado

Si tienes los datos en Excel o CSV, usa este formato:

```
Referencia	Título	País	Tipo	Fecha Publicado	Fecha Cierre	URL
UNGM-2026-001	Supply of Cement and Materials	Honduras	Materials	2026-08-20	2026-09-15	https://www.ungm.org/...
UNGM-2026-002	Construction Services - Building	Honduras	Construction	2026-08-18	2026-09-18	https://www.ungm.org/...
```

**Importante:** Separar con **tabulación** (Tab), no espacios

### 🔄 Opción 2: Google Sheets / Copy-Paste

Si puedes ver los procesos en UNGM:

1. Selecciona la tabla en UNGM
2. Copia (Ctrl+C)
3. Pégalo en un documento de texto
4. Adapta al formato CSV
5. Usa: `python3 scripts/importar_ungm_manual.py tu_archivo.csv`

### ⚙️ Opción 3: Script en Browser (para ti)

Si tienes acceso a un navegador con JavaScript, copia este código en la consola (F12):

```javascript
// Extrae todos los procesos visibles de la tabla
const rows = document.querySelectorAll('table tbody tr');
const datos = [];

rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    if (cells.length >= 6) {
        datos.push({
            referencia: cells[0].textContent.trim(),
            titulo: cells[1].textContent.trim(),
            pais: cells[2].textContent.trim(),
            tipo: cells[3].textContent.trim(),
            fecha_publicado: cells[4].textContent.trim(),
            fecha_cierre: cells[5].textContent.trim(),
            url: cells[6]?.querySelector('a')?.href || ''
        });
    }
});

// Descarga como JSON
console.log(JSON.stringify(dados, null, 2));
// O guarda en archivo:
download(JSON.stringify(dados, null, 2), "ungm.json", "application/json");

function download(content, filename, type) {
    const element = document.createElement("a");
    element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(content));
    element.setAttribute("download", filename);
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}
```

## 📊 Una Vez Tengas los Datos

Después de importar procesos con alguna de las opciones anteriores:

```bash
# 1. Generar reporte HTML
python3 scripts/generar_reporte_ungm.py

# 2. Ver en navegador
open reportes/ungm-construccion.html

# 3. Sincronizar con Git
git add data/ungm-honduras.json reportes/ungm-construccion.html
git commit -m "Actualizar procesos UNGM Honduras"
git push
```

## 🔗 Links Útiles

- **UNGM:** https://www.ungm.org/Public/Notice
- **Filtros UNGM:** https://www.ungm.org/Public/Notice (en página, aplica filtros)
- **Datos Actuales:** `data/ungm-honduras.json`
- **Reporte:** `reportes/ungm-construccion.html`

## ❓ Preguntas Frecuentes

**P:** ¿Cuántos procesos hay para Honduras?  
R: Depende de los filtros que apliques en UNGM. Puede haber 5-20+ procesos vigentes.

**P:** ¿Puedo automatizar esto?  
R: Sí, si UNGM proporciona una API pública. De lo contrario, requiere navegador real con JavaScript.

**P:** ¿Con qué frecuencia se actualizan?  
R: UNGM se actualiza diariamente. Se recomienda actualizar 1-2 veces por semana.

## 📝 Ejemplo Completo

```bash
# 1. Usar modo interactivo
python3 scripts/importar_ungm_manual.py

# Ingresa los procesos que ves en UNGM...
# Escribe "fin" para terminar

# 2. Se genera automáticamente: data/ungm-honduras.json

# 3. Generar reporte
python3 scripts/generar_reporte_ungm.py

# 4. Ver resultado
open reportes/ungm-construccion.html
```

---

**Limitación Técnica:** Este ambiente no tiene acceso a navegadores Chrome/Chromium completos con soporte para JavaScript remoto. Por eso se requiere extracción manual o desde archivo CSV.
