#!/usr/bin/env python3
"""
Script de debugging - Muestra exactamente el contenido de las celdas
"""

import sys
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Error: pip install playwright")
    sys.exit(1)

def debug_tabla():
    """Muestra contenido exacto de la tabla"""

    print("="*100)
    print("🔍 DEBUG - CONTENIDO EXACTO DE LA TABLA SICC")
    print("="*100 + "\n")

    url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navegar
            page.goto(url, wait_until='load')
            print("✅ Página cargada\n")

            import time
            time.sleep(2)

            # Seleccionar Obras
            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipoAdquisicion', '2')
            print("✅ Filtro 'Obras' seleccionado\n")

            # Buscar
            page.click('#ctl00_cphCuerpo_wpParametros_btnBuscar')
            page.wait_for_load_state('networkidle')
            print("✅ Búsqueda realizada\n")

            time.sleep(2)

            # Encontrar tabla
            tablas = page.query_selector_all('table')
            print(f"📊 Total tablas: {len(tablas)}\n")

            # Analizar cada tabla
            for idx, tabla in enumerate(reversed(tablas)):
                filas = tabla.query_selector_all('tr')

                if len(filas) > 2:
                    print(f"[TABLA {len(tablas)-idx}] Filas: {len(filas)}")

                    # Mostrar header
                    header_celdas = filas[0].query_selector_all('th, td')
                    print(f"  Headers ({len(header_celdas)}):")
                    for idx_h, celda in enumerate(header_celdas[:8]):
                        contenido = celda.text_content().strip()[:40]
                        print(f"    [{idx_h}] '{contenido}'")

                    # Mostrar primeras 3 filas de datos
                    print(f"  Datos ({len(filas)-1} filas):")
                    for idx_f, fila in enumerate(filas[1:4]):
                        celdas = fila.query_selector_all('td')
                        print(f"    Fila {idx_f}:")
                        for idx_c, celda in enumerate(celdas[:8]):
                            contenido = celda.text_content().strip()[:60]
                            print(f"      [{idx_c}] '{contenido}'")

                    print()

        except Exception as e:
            print(f"❌ Error: {e}")

        finally:
            browser.close()

    print("="*100)

if __name__ == "__main__":
    debug_tabla()
