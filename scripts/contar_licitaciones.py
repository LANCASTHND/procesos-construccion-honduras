#!/usr/bin/env python3
"""
Contador rápido: ¿Cuántas licitaciones vigentes construcción existen en SICC?
Búsqueda global sin filtro institución
"""

import time
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ pip install playwright")
    exit(1)

def contar():
    print("\n" + "="*70)
    print("CONTADOR DE LICITACIONES VIGENTES CONSTRUCCIÓN")
    print("="*70 + "\n")

    palabras = ['construcción', 'obra', 'remodelación', 'ingeniería', 'pavimentación',
                'infraestructura', 'mejoramiento', 'vial', 'carretera', 'puente']

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(30000)

            print("📍 Navegando a SICC...")
            page.goto("http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx",
                     wait_until='load')
            time.sleep(1)

            print("🔍 Buscando licitaciones vigentes (sin filtro institución)...\n")

            # No seleccionar institución = búsqueda global
            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipos', 'licitacion')
            time.sleep(1)

            ahora = datetime.now()
            total_encontrados = 0
            construccion_count = 0
            pagina = 1

            while pagina <= 50:
                try:
                    filas = page.query_selector_all('table[id*="gvResultados"] tbody tr')
                    if not filas:
                        if pagina == 1:
                            print("   ⚠️  No hay resultados")
                        break

                    print(f"   📄 Página {pagina}: {len(filas)} registros", end="")

                    for fila in filas:
                        try:
                            celdas = fila.query_selector_all('td')
                            if len(celdas) < 8:
                                continue

                            expediente = celdas[1].text_content().strip()
                            descripcion = celdas[2].text_content().strip()
                            cierre_text = celdas[5].text_content().strip()

                            # Contar vigentes
                            try:
                                fecha_cierre = datetime.strptime(cierre_text, "%d/%m/%Y")
                                if fecha_cierre.year >= 2026 and fecha_cierre >= ahora:
                                    total_encontrados += 1

                                    # Contar construcción
                                    texto = f"{expediente} {descripcion}".lower()
                                    if any(p in texto for p in palabras):
                                        construccion_count += 1

                            except:
                                pass

                        except:
                            continue

                    # Siguiente página
                    try:
                        btn = page.query_selector('a[id*="lnkSiguiente"]')
                        if not btn or 'disabled' in btn.get_attribute('class', ''):
                            print()
                            break

                        print(" ✓")
                        btn.click()
                        time.sleep(0.5)
                        pagina += 1

                    except:
                        print()
                        break

                except Exception as e:
                    print(f"❌ Error página {pagina}: {e}")
                    break

            browser.close()

            print("\n" + "="*70)
            print(f"📊 RESULTADOS:")
            print(f"   Total licitaciones vigentes 2026+:        {total_encontrados}")
            print(f"   Licitaciones construcción/ingeniería:     {construccion_count}")
            print(f"   Cobertura actual (nuestros datos):       20")
            print(f"   DIFERENCIA:                              {construccion_count - 20} procesos sin capturar")
            print("="*70 + "\n")

            return construccion_count

    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

if __name__ == "__main__":
    contar()
