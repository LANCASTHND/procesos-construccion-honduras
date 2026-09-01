#!/usr/bin/env python3
"""
Extractor v6 - Dinámico: Extrae TODAS las instituciones de SICC
Automáticamente descubre todas las instituciones disponibles en el dropdown
"""

import json
import sys
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
import os

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Error: pip install playwright")
    sys.exit(1)

class SICCExtractorV6:
    """Extractor v6 - Dinámico con descubrimiento automático de instituciones"""

    def __init__(self):
        self.base_url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"
        self.contactos = {
            "UNAH": "unah-compras@unah.edu.hn",
            "UNA": "compras@una.hn",
            "UNACIFOR": "compras@unacifor.hn",
            "SIT": "licitaciones@sit.gob.hn",
            "SEDENA": "compras@sedena.mil.hn",
            "SESEGU": "compras@sesegu.gob.hn",
            "IHT": "compras@iht.hn",
            "TEGUCIGALPA": "compras@tegucigalpa.gob.hn",
            "SAN PEDRO SULA": "compras@sanpedrosula.gob.hn",
            "LA CEIBA": "compras@laceiba.gob.hn",
            "DANLI": "compras@danli.gob.hn",
            "EL RAMA": "compras@elrama.gob.hn",
            "COMAYAGUA": "compras@comayagua.gob.hn",
            "CHOLOMA": "compras@munichol.hn",
            "CUERPO DE BOMBEROS": "compras@cuerpodbomberos.hn",
            "PRONADERS": "compras@pronaders.hn",
            "DISTRITO CENTRAL": "compras@distritocental.hn",
        }

    def _obtener_todas_instituciones(self, page) -> Dict[str, str]:
        """Extrae dinámicamente TODAS las instituciones del dropdown de SICC"""
        print("   🔍 Descubriendo instituciones en SICC...")

        instituciones = {}

        try:
            page.goto(self.base_url, wait_until='load')
            time.sleep(1)

            # Buscar el select de entidades
            try:
                select_elem = page.query_selector('#ctl00_cphCuerpo_wpParametros_ddlEntidades')
                if not select_elem:
                    print("   ❌ No se encontró dropdown de instituciones")
                    return instituciones

                # Obtener todas las opciones
                opciones = page.query_selector_all('#ctl00_cphCuerpo_wpParametros_ddlEntidades option')

                print(f"   📋 Encontradas {len(opciones)} opciones en dropdown")

                for opcion in opciones:
                    try:
                        value = opcion.get_attribute('value')
                        texto = opcion.text_content().strip()

                        # Saltar opciones vacías o por defecto
                        if not value or value == '0' or 'seleccione' in texto.lower():
                            continue

                        # Limpiar nombre
                        nombre_limpio = texto.strip()
                        if nombre_limpio and len(nombre_limpio) > 2:
                            instituciones[value] = nombre_limpio
                            print(f"      ✓ {nombre_limpio}")

                    except Exception as e:
                        continue

                print(f"   ✅ Total instituciones descubiertas: {len(instituciones)}\n")

            except Exception as e:
                print(f"   ❌ Error al extraer instituciones: {e}\n")

        except Exception as e:
            print(f"   ❌ Error: {e}\n")

        return instituciones

    def _extraer_con_paginacion(self, page, tipo: str = "licitacion") -> List[Dict[str, Any]]:
        """Extrae procesos manejando TODAS las páginas de resultados"""
        procesos_totales = []
        pagina_actual = 1
        ahora = datetime.now()

        while True:
            print(f"      📄 Página {pagina_actual}...", end=" ", flush=True)

            try:
                # Extraer procesos de página actual
                procesos_pagina = self._extraer_procesos(page, tipo, ahora)

                if not procesos_pagina:
                    print("vacía", flush=True)
                    break

                procesos_totales.extend(procesos_pagina)
                print(f"✓ {len(procesos_pagina)}", flush=True)

                # Buscar botón "Siguiente"
                try:
                    btn_siguiente = page.query_selector('a[title="Siguiente"]')
                    if not btn_siguiente:
                        btn_siguiente = page.query_selector('input[title="Siguiente"]')
                    if not btn_siguiente:
                        btn_siguiente = page.query_selector('[id*="lbtnSiguiente"]')
                    if not btn_siguiente:
                        # Intenta por texto
                        links = page.query_selector_all('a')
                        for link in links:
                            if "siguiente" in link.text_content().lower():
                                btn_siguiente = link
                                break

                    if btn_siguiente and btn_siguiente.is_enabled():
                        btn_siguiente.click(no_wait_after=True)
                        time.sleep(1.5)
                        pagina_actual += 1
                    else:
                        break

                except Exception as e:
                    break

            except Exception as e:
                print(f"error", flush=True)
                break

        return procesos_totales

    def extraer_todos_procesos_dinamico(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extrae TODOS los procesos de TODAS las instituciones dinámicamente"""
        print("=" * 70)
        print("🚀 EXTRACTOR V6 - DINÁMICO CON TODAS LAS INSTITUCIONES")
        print("=" * 70)
        print()

        resultado = {
            "licitaciones": [],
            "compras_menores": [],
            "instituciones_procesadas": 0,
            "instituciones_fallidas": 0,
        }

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(30000)

            try:
                # Paso 1: Obtener todas las instituciones
                instituciones = self._obtener_todas_instituciones(page)

                if not instituciones:
                    print("❌ No se pudieron obtener instituciones\n")
                    browser.close()
                    return resultado

                # Paso 2: Procesar LICITACIONES
                print("\n" + "=" * 70)
                print("📋 EXTRAYENDO LICITACIONES")
                print("=" * 70 + "\n")

                enlaces_licitaciones = set()

                for inst_code, inst_nombre in instituciones.items():
                    print(f"   🏛️  {inst_nombre}...", end=" ", flush=True)

                    try:
                        page.goto(self.base_url, wait_until='load')
                        time.sleep(1)

                        # Filtro Obras
                        try:
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipoAdquisicion', '2')
                        except:
                            pass

                        # Filtro Institución
                        try:
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlEntidades', inst_code)
                        except:
                            print("❌", flush=True)
                            resultado["instituciones_fallidas"] += 1
                            continue

                        # Buscar
                        try:
                            page.click('#ctl00_cphCuerpo_wpParametros_btnBuscar')
                            page.wait_for_load_state('networkidle')
                            time.sleep(1)
                        except:
                            print("❌", flush=True)
                            resultado["instituciones_fallidas"] += 1
                            continue

                        # Extraer con pagination
                        procesos = self._extraer_con_paginacion(page, "licitacion")

                        # Agregar sin duplicados
                        nuevos = 0
                        for p in procesos:
                            enlace = p.get('link', '')
                            if enlace and enlace not in enlaces_licitaciones:
                                resultado["licitaciones"].append(p)
                                enlaces_licitaciones.add(enlace)
                                nuevos += 1
                            elif not enlace:
                                resultado["licitaciones"].append(p)
                                nuevos += 1

                        print(f"✓ {nuevos} procesos", flush=True)
                        resultado["instituciones_procesadas"] += 1

                    except Exception as e:
                        print(f"❌ {e}", flush=True)
                        resultado["instituciones_fallidas"] += 1
                        continue

                # Paso 3: Procesar COMPRAS MENORES
                print("\n" + "=" * 70)
                print("📦 EXTRAYENDO COMPRAS MENORES")
                print("=" * 70 + "\n")

                enlaces_compras = set()

                for inst_code, inst_nombre in instituciones.items():
                    print(f"   🏛️  {inst_nombre}...", end=" ", flush=True)

                    try:
                        page.goto(self.base_url, wait_until='load')
                        time.sleep(1)

                        # Filtro Compra Menor
                        try:
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlModalidad', '2')
                        except:
                            pass

                        # Filtro Institución
                        try:
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlEntidades', inst_code)
                        except:
                            print("❌", flush=True)
                            continue

                        # Buscar
                        try:
                            page.click('#ctl00_cphCuerpo_wpParametros_btnBuscar', no_wait_after=True)
                            time.sleep(2)
                        except:
                            print("❌", flush=True)
                            continue

                        # Extraer con pagination
                        procesos = self._extraer_con_paginacion(page, "compra_menor")

                        # Agregar sin duplicados
                        nuevos = 0
                        for p in procesos:
                            enlace = p.get('link', '')
                            if enlace and enlace not in enlaces_compras:
                                resultado["compras_menores"].append(p)
                                enlaces_compras.add(enlace)
                                nuevos += 1
                            elif not enlace:
                                resultado["compras_menores"].append(p)
                                nuevos += 1

                        print(f"✓ {nuevos} procesos", flush=True)

                    except Exception as e:
                        print(f"❌", flush=True)
                        continue

                # Paso 4: Enriquecer con descripciones
                print("\n" + "=" * 70)
                print("📝 ENRIQUECIENDO CON DESCRIPCIONES")
                print("=" * 70 + "\n")

                all_procesos = resultado["licitaciones"] + resultado["compras_menores"]
                self._enriquecer_con_objeto(all_procesos, browser)

            except Exception as e:
                print(f"   ❌ Error general: {e}\n")

            finally:
                browser.close()

        return resultado

    def _enriquecer_con_objeto(self, procesos: List[Dict], browser) -> None:
        """Enriquece procesos con objeto (descripción)"""
        vigentes = [p for p in procesos if p.get('estado_proceso') == 'vigente' and p.get('link')]

        if not vigentes:
            return

        print(f"   📝 Extrayendo descripciones para {len(vigentes)} procesos vigentes...")

        contador = 0
        for i, proceso in enumerate(vigentes, 1):
            try:
                objeto = self._extraer_objeto(browser, proceso['link'])
                if objeto:
                    proceso['objeto'] = objeto
                    contador += 1
                if i % 20 == 0:
                    print(f"      ✓ {i}/{len(vigentes)} procesados ({contador} descripciones)...")
            except:
                pass

            time.sleep(0.2)

        print(f"      ✓ {contador}/{len(vigentes)} descripciones extraídas\n")

    def _extraer_objeto(self, browser, link: str) -> str:
        """Extrae objeto de página de detalle"""
        detail_page = None
        try:
            if not link:
                return ""

            if link.startswith('/'):
                url = "http://sicc.honducompras.gob.hn" + link
            elif not link.startswith('http'):
                url = "http://sicc.honducompras.gob.hn/HC/procesos/" + link
            else:
                url = link

            detail_page = browser.new_page()
            detail_page.set_default_timeout(10000)

            detail_page.goto(url, wait_until='domcontentloaded', timeout=10000)
            time.sleep(0.3)

            try:
                objeto_rows = detail_page.query_selector_all('table tr')

                for fila in objeto_rows:
                    celdas = fila.query_selector_all('td')
                    if len(celdas) >= 2:
                        label_text = celdas[0].inner_text().strip()

                        if label_text == 'Objeto':
                            valor_celda = celdas[1].text_content().strip()

                            if valor_celda and len(valor_celda) > 10:
                                if 'Objeto' in valor_celda:
                                    idx = valor_celda.rfind('Objeto')
                                    if idx != -1:
                                        objeto = valor_celda[idx + 6:].strip()
                                        objeto = objeto.lstrip('"\' :')
                                        objeto = ' '.join(objeto.split())
                                        if len(objeto) > 10:
                                            return objeto[:300]
                                else:
                                    if not any(keyword in valor_celda for keyword in ['Expediente', 'Entidad', 'Sys.', '/*', 'CDATA']):
                                        objeto = ' '.join(valor_celda.split())
                                        if len(objeto) > 10:
                                            return objeto[:300]
            except:
                pass

            return ""
        except Exception as e:
            return ""
        finally:
            if detail_page:
                try:
                    detail_page.close()
                except:
                    pass

    def _extraer_procesos(self, page, tipo: str = "licitacion", ahora: datetime = None) -> List[Dict[str, Any]]:
        """Extrae procesos de la tabla actual (una sola página)"""
        if ahora is None:
            ahora = datetime.now()

        procesos = []

        try:
            for i in range(5):
                try:
                    time.sleep(0.5)
                    page.query_selector('body')
                    break
                except:
                    if i == 4:
                        return procesos

            tablas = page.query_selector_all('table')
            tabla_procesos = None

            for tabla in tablas:
                filas = tabla.query_selector_all('tr')
                if len(filas) > 2:
                    primera_fila = filas[0]
                    header_text = primera_fila.text_content()
                    if ("Expediente" in header_text or "Adquisición" in header_text):
                        tabla_procesos = tabla
                        break

            if not tabla_procesos:
                tablas_validas = [t for t in tablas if len(t.query_selector_all('tr')) > 3]
                if tablas_validas:
                    tabla_procesos = max(tablas_validas, key=lambda t: len(t.query_selector_all('tr')))

            if not tabla_procesos:
                return procesos

            filas = tabla_procesos.query_selector_all('tr')
            datos_filas = filas[1:] if len(filas) > 1 else []

            for fila in datos_filas:
                try:
                    celdas = fila.query_selector_all('td')
                    if len(celdas) < 4:
                        continue

                    expediente_texto = celdas[0].text_content().strip() if len(celdas) > 0 else ""
                    etapa = celdas[1].text_content().strip() if len(celdas) > 1 else ""
                    modalidad = celdas[2].text_content().strip() if len(celdas) > 2 else ""
                    vigencia_texto = celdas[3].text_content().strip() if len(celdas) > 3 else ""

                    link = ""
                    if len(celdas) > 4:
                        link_elem = celdas[4].query_selector('a')
                        if link_elem:
                            link = link_elem.get_attribute('href') or ""

                    if not expediente_texto or not vigencia_texto:
                        continue

                    expediente = expediente_texto.replace("Expediente:", "").strip()
                    if not expediente:
                        continue

                    fecha_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', vigencia_texto)
                    if not fecha_match:
                        continue

                    fecha_inicio_str = fecha_match.group(0)
                    fecha_cierre_str = re.search(r'Cierre:\s*(\d{1,2}/\d{1,2}/\d{4})', vigencia_texto)
                    if not fecha_cierre_str:
                        continue

                    fecha_cierre = fecha_cierre_str.group(1)

                    try:
                        fecha_cierre_dt = datetime.strptime(fecha_cierre, "%d/%m/%Y")
                        dias = (fecha_cierre_dt - ahora).days

                        # FILTRO: Solo incluir procesos vigentes (dias >= 0) y de 2026 en adelante
                        if dias < 0 or fecha_cierre_dt.year < 2026:
                            continue
                    except:
                        continue

                    # Extraer institución del expediente
                    institucion = self._extraer_institucion(expediente)
                    contacto = self.contactos.get(institucion, "info@institucion.hn")

                    proceso = {
                        "expediente": expediente.replace('\n', '').strip(),
                        "descripcion": "Proceso " + tipo.replace('_', ' ').title(),
                        "institucion": institucion,
                        "etapa": etapa,
                        "modalidad": modalidad,
                        "monto": 0,
                        "cierre": fecha_cierre,
                        "fecha_inicio": fecha_inicio_str,
                        "contacto": contacto,
                        "link": link,
                        "dias_para_cierre": dias,
                        "tipo_licitacion": tipo,
                        "objeto": "Descripción disponible",
                        "estado_proceso": "vigente",
                        "fecha_extraccion": datetime.now().strftime("%Y-%m-%d"),
                    }

                    procesos.append(proceso)

                except Exception as e:
                    continue

            return procesos

        except Exception as e:
            return procesos

    def _extraer_institucion(self, expediente: str) -> str:
        """Extrae institución del expediente"""
        expediente_upper = expediente.upper().strip()
        expediente_clean = ' '.join(expediente_upper.split())

        for sigla in self.contactos.keys():
            sigla_upper = sigla.upper()
            if sigla_upper in expediente_clean:
                return sigla

        if "BOMBEROS" in expediente_clean or "CUERPO" in expediente_clean:
            return "CUERPO DE BOMBEROS"
        elif "MUNICIPAL" in expediente_clean or "MUNICIPALI" in expediente_clean or "DISTRITO" in expediente_clean:
            return "MUNICIPALIDADES"
        elif "SPE" in expediente_clean:
            return "MUNICIPALIDADES"

        return "VARIAS"


def main():
    extractor = SICCExtractorV6()
    resultado = extractor.extraer_todos_procesos_dinamico()

    # Guardar licitaciones
    datos_lic = {
        "metadata": {
            "tipo": "licitaciones",
            "total_procesos": len(resultado["licitaciones"]),
            "inversion_total": 0,
            "moneda": "Lempiras (L.)",
            "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "vigentes",
            "cobertura": "Honduras - Todas las Instituciones SICC",
            "fuente": "SICC Honduras Compras",
            "metodo_extraccion": "playwright-dinamico-v6-todas-instituciones"
        },
        "procesos": resultado["licitaciones"]
    }

    with open("data/licitaciones.json", "w") as f:
        json.dump(datos_lic, f, indent=2, ensure_ascii=False)

    print(f"✅ Guardado: data/licitaciones.json")

    # Guardar compras menores
    datos_cm = {
        "metadata": {
            "tipo": "compras_menores",
            "total_procesos": len(resultado["compras_menores"]),
            "inversion_total": 0,
            "moneda": "Lempiras (L.)",
            "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "vigentes",
            "cobertura": "Honduras - Todas las Instituciones SICC",
            "fuente": "SICC Honduras Compras",
            "metodo_extraccion": "playwright-dinamico-v6-todas-instituciones"
        },
        "procesos": resultado["compras_menores"]
    }

    with open("data/compras-menores.json", "w") as f:
        json.dump(datos_cm, f, indent=2, ensure_ascii=False)

    print(f"✅ Guardado: data/compras-menores.json")

    # Resumen
    print(f"""
[──────────────────────────────────────────────────────────]
📋 RESUMEN FINAL - EXTRACTOR V6 DINÁMICO
[──────────────────────────────────────────────────────────]
✅ Licitaciones: {len(resultado["licitaciones"])}
✅ Compras menores: {len(resultado["compras_menores"])}
✅ Total procesos vigentes: {len(resultado["licitaciones"]) + len(resultado["compras_menores"])}
✅ Instituciones procesadas: {resultado["instituciones_procesadas"]}
❌ Instituciones fallidas: {resultado["instituciones_fallidas"]}
⏰ Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
============================================================
    """)


if __name__ == "__main__":
    main()
