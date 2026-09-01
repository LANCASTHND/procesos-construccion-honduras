#!/usr/bin/env python3
"""
Identifica las instituciones más activas en SICC
Búsqueda global para contar procesos por institución
"""

import time
from datetime import datetime
from collections import defaultdict

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ pip install playwright")
    exit(1)

def identificar():
    print("\n" + "="*70)
    print("IDENTIFICAR INSTITUCIONES MÁS ACTIVAS")
    print("="*70 + "\n")

    instituciones_core = [
        "UNAH", "UNA", "UNACIFOR", "SIT", "SEDENA", "SESEGU", "IHT",
        "TEGUCIGALPA", "SAN PEDRO SULA", "LA CEIBA", "DANLI",
        "EL RAMA", "COMAYAGUA", "CHOLOMA"
    ]

    nuevas = ["MUNICIPALIDAD DEL DISTRITO CENTRAL", "PRONADERS"]

    contador = defaultdict(int)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(30000)

            print("📍 Navegando a SICC (búsqueda global)...\n")
            page.goto("http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx",
                     wait_until='load', timeout=30000)
            time.sleep(1)

            print("🔍 Contando procesos por institución...\n")

            try:
                page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipos', 'licitacion')
                time.sleep(1)
            except:
                print("⚠️  No se pudo seleccionar tipo, intentando búsqueda general...")

            ahora = datetime.now()
            pagina = 1
            total_procesos = 0

            while pagina <= 100:
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

                            cierre_text = celdas[5].text_content().strip() if len(celdas) > 5 else ""
                            institucion_raw = celdas[7].text_content().strip() if len(celdas) > 7 else ""

                            # Filtrar fecha 2026+
                            try:
                                fecha_cierre = datetime.strptime(cierre_text, "%d/%m/%Y")
                                if fecha_cierre.year < 2026 or fecha_cierre < ahora:
                                    continue
                            except:
                                continue

                            # Extraer institución
                            institucion = institucion_raw.split('-')[0].strip() if '-' in institucion_raw else institucion_raw.strip()

                            if institucion:
                                contador[institucion] += 1
                                total_procesos += 1

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

            # Ordenar por actividad
            ordenadas = sorted(contador.items(), key=lambda x: x[1], reverse=True)

            print(f"\n📊 Total procesos vigentes 2026+: {total_procesos}")
            print(f"📊 Total instituciones encontradas: {len(contador)}\n")

            print("🏢 TOP 20 INSTITUCIONES MÁS ACTIVAS:\n")

            for i, (inst, count) in enumerate(ordenadas[:20], 1):
                marcado = ""
                if inst in instituciones_core:
                    marcado = " ✓ (CORE)"
                elif inst in nuevas:
                    marcado = " ⭐ (NUEVA)"
                print(f"   {i:2d}. {inst:50s} ({count:3d} procesos){marcado}")

            print("\n" + "="*70)
            print("RECOMENDACIÓN:")
            print("="*70)
            print("\n✅ Instituciones CORE (14):")
            for inst in instituciones_core:
                print(f"   • {inst}")

            print("\n⭐ Instituciones NUEVAS (2):")
            for inst in nuevas:
                print(f"   • {inst}")

            print("\n📈 Instituciones TOP por ACTIVIDAD (14 más activas):")
            count_seleccionadas = 0
            for inst, count in ordenadas:
                if inst not in instituciones_core and inst not in nuevas:
                    if count_seleccionadas < 14:
                        print(f"   • {inst} ({count} procesos)")
                        count_seleccionadas += 1
                    if count_seleccionadas >= 14:
                        break

            print("\n" + "="*70)
            print("TOTAL: 14 (core) + 2 (nuevas) + 14 (activas) = 30 instituciones")
            print("="*70 + "\n")

            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    identificar()
