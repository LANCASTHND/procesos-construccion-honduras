#!/usr/bin/env python3
"""
Script de introspección - Descubre la estructura real del HTML de SICC
Usa Playwright para obtener selectores CSS correctos
"""

import sys
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Error: pip install playwright")
    sys.exit(1)

def inspeccionar_sicc():
    """Inspecciona estructura de SICC con Playwright"""

    print("="*80)
    print("🔍 INTROSPECCIÓN SICC - Descubriendo selectores correctos")
    print("="*80 + "\n")

    url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(30000)

        try:
            print("[1] Navegando a SICC...\n")
            page.goto(url, wait_until='load')
            print("✅ Página cargada\n")

            # Esperar a que se cargue completamente
            import time
            time.sleep(3)

            # Buscar todos los selects (dropdowns)
            print("[2] Buscando dropdowns...\n")
            selects = page.query_selector_all('select')
            print(f"✅ Encontrados {len(selects)} dropdowns:\n")
            for idx, select in enumerate(selects):
                select_id = select.get_attribute('id')
                select_name = select.get_attribute('name')
                print(f"   [{idx}] ID: {select_id}")
                print(f"       Name: {select_name}")

                # Opciones del select
                opciones = select.query_selector_all('option')
                print(f"       Opciones: {len(opciones)}")
                if len(opciones) <= 20:
                    for opt in opciones[:5]:
                        opt_value = opt.get_attribute('value')
                        opt_text = opt.text_content()
                        print(f"         • {opt_value} = {opt_text}")
                print()

            # Buscar botones de búsqueda
            print("[3] Buscando botones de búsqueda...\n")
            buttons = page.query_selector_all('button')
            inputs = page.query_selector_all('input[type="submit"], input[type="button"]')
            print(f"✅ Encontrados {len(buttons)} buttons y {len(inputs)} inputs:\n")

            for btn in buttons[:5]:
                btn_id = btn.get_attribute('id')
                btn_name = btn.get_attribute('name')
                btn_text = btn.text_content()
                print(f"   Button - ID: {btn_id}, Name: {btn_name}, Texto: {btn_text}")

            for inp in inputs[:5]:
                inp_id = inp.get_attribute('id')
                inp_name = inp.get_attribute('name')
                inp_value = inp.get_attribute('value')
                print(f"   Input - ID: {inp_id}, Name: {inp_name}, Value: {inp_value}")

            print()

            # Buscar tablas
            print("[4] Buscando tablas de datos...\n")
            tables = page.query_selector_all('table')
            print(f"✅ Encontradas {len(tables)} tablas:\n")

            for idx, table in enumerate(tables[:3]):
                table_id = table.get_attribute('id')
                table_class = table.get_attribute('class')
                rows = table.query_selector_all('tr')
                print(f"   Tabla [{idx}]:")
                print(f"     ID: {table_id}")
                print(f"     Class: {table_class}")
                print(f"     Filas: {len(rows)}")

                if len(rows) > 0:
                    header_cells = rows[0].query_selector_all('th, td')
                    print(f"     Headers: {len(header_cells)}")
                    for cell in header_cells[:5]:
                        print(f"       • {cell.text_content()[:30]}")

                print()

            # Buscar divs principales
            print("[5] Estructura de divs principales...\n")
            main_divs = page.query_selector_all('div[id*="ContentPlaceHolder"], div[id*="content"], div.content')
            print(f"✅ Encontrados {len(main_divs)} divs de contenido:\n")

            for div in main_divs[:5]:
                div_id = div.get_attribute('id')
                div_class = div.get_attribute('class')
                children = div.query_selector_all('> *')
                print(f"   Div - ID: {div_id}, Class: {div_class}, Hijos: {len(children)}")

            print()

            # Contar elementos de datos después de clic simulado
            print("[6] Intentando simular búsqueda...\n")

            # Intentar hacer clic en botón de búsqueda si existe
            try:
                buscar_btn = page.query_selector('button:has-text("Buscar"), input[value*="Buscar"]')
                if buscar_btn:
                    print("✅ Botón Buscar encontrado, haciendo clic...")
                    buscar_btn.click()
                    page.wait_for_load_state('networkidle')
                    print("✅ Búsqueda realizada\n")

                    # Contar resultados
                    time.sleep(2)
                    tablas_resultado = page.query_selector_all('table')
                    print(f"Tablas después de búsqueda: {len(tablas_resultado)}")

                    for tabla in tablas_resultado:
                        filas = tabla.query_selector_all('tr')
                        if len(filas) > 1:
                            print(f"  Tabla con {len(filas)} filas encontrada")
                            # Mostrar primer fila de datos
                            primera_fila = filas[0] if len(filas) > 0 else None
                            if primera_fila:
                                celdas = primera_fila.query_selector_all('td, th')
                                print(f"  Contenido fila 0: {[c.text_content()[:20] for c in celdas[:5]]}")

            except Exception as e:
                print(f"⚠️  No se pudo simular búsqueda: {e}\n")

        except Exception as e:
            print(f"❌ Error: {e}")

        finally:
            browser.close()

    print("\n" + "="*80)
    print("✅ Introspección completada")
    print("="*80)
    print("\nUSO: Usa los selectores encontrados para mejorar extractor_honduras_compras_v2.py")

if __name__ == "__main__":
    inspeccionar_sicc()
