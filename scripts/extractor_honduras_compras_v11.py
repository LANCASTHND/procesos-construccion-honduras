#!/usr/bin/env python3
"""
Extractor v11 - v5 mejorado + SESAL
Extrae licitaciones y compras menores preservando modalidad (pública/privada/internacional)
"""

import json
import sys
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Error: pip install playwright")
    sys.exit(1)

class SICCExtractorV11:
    """Extractor v11 - v5 mejorado con SESAL y modalidades"""

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
            "SESAL": "compras@sesal.gob.hn",
            "TEGUCIGALPA": "compras@tegucigalpa.gob.hn",
            "SAN PEDRO SULA": "compras@sanpedrosula.gob.hn",
            "LA CEIBA": "compras@laceiba.gob.hn",
            "DANLI": "compras@danli.gob.hn",
            "EL RAMA": "compras@elrama.gob.hn",
            "COMAYAGUA": "compras@comayagua.gob.hn",
            "CHOLOMA": "compras@munichol.hn",
            "CUERPO DE BOMBEROS": "compras@cuerpodbomberos.hn",
        }
        self.institution_map = {
            "33": ("Universidad Nacional Autónoma de Honduras (UNAH)", "UNAH"),
            "34": ("Universidad Nacional de Agricultura (UNA)", "UNA"),
            "52": ("Universidad Nacional de Ciencias Forestales (UNACIFOR)", "UNACIFOR"),
            "521": ("Secretaría de Estado en los Despachos de Infraestructura y Transporte (SIT)", "SIT"),
            "20": ("Secretaría de Estado en el Despacho de Defensa Nacional SEDENA)", "SEDENA"),
            "40": ("Secretaría de Estado en el Despacho de Seguridad (SESEGU)", "SESEGU"),
            "493": ("Instituto Hondureño de Turismo (IHT)", "IHT"),
            "395": ("Secretaría de Salud (SESAL)", "SESAL"),
            "103": ("Municipalidad de Tegucigalpa", "TEGUCIGALPA"),
            "106": ("Municipalidad de San Pedro Sula, Cortés", "SAN PEDRO SULA"),
            "107": ("Municipalidad de La Ceiba, Atlantida", "LA CEIBA"),
            "185": ("Municipalidad de Danli, El Paraíso", "DANLI"),
            "102": ("Municipalidad de Comayagua, Comayagua", "COMAYAGUA"),
            "151": ("Municipalidad de Choloma, Cortés", "CHOLOMA"),
            "405": ("Cuerpo de Bomberos de Honduras (CBH)", "CUERPO DE BOMBEROS"),
        }

    def _extraer_con_paginacion(self, page, tipo: str = "licitacion") -> List[Dict[str, Any]]:
        """Extrae procesos manejando TODAS las páginas de resultados"""
        procesos_totales = []
        pagina_actual = 1
        max_intentos_sin_nuevos = 3
        intentos = 0

        while True:
            print(f"      📄 Página {pagina_actual}...", end=" ", flush=True)

            try:
                # Extraer procesos de página actual
                procesos_pagina = self._extraer_procesos(page, tipo)

                if not procesos_pagina:
                    print("vacía", flush=True)
                    break

                procesos_totales.extend(procesos_pagina)
                print(f"✓ {len(procesos_pagina)}", flush=True)

                # Buscar botón "Siguiente"
                try:
                    # Selector común para botón siguiente en ASP.NET
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
                        print("      📄 No hay más páginas", flush=True)
                        break

                except Exception as e:
                    print("      📄 No hay más páginas", flush=True)
                    break

            except Exception as e:
                print(f"error", flush=True)
                break

        return procesos_totales

    def extraer_licitaciones_completo(self) -> List[Dict[str, Any]]:
        """Extrae TODAS las licitaciones por institución CON PAGINATION"""
        print("🔍 Extrayendo licitaciones por institución (con pagination)...\n")

        procesos_totales = []
        enlaces_vistos = set()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(30000)

            try:
                for inst_code, (inst_nombre, inst_sigla) in self.institution_map.items():
                    print(f"   🏛️  {inst_sigla}...", end=" ", flush=True)

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
                            continue

                        # Buscar
                        try:
                            page.click('#ctl00_cphCuerpo_wpParametros_btnBuscar')
                            page.wait_for_load_state('networkidle')
                            time.sleep(1)
                        except:
                            print("❌", flush=True)
                            continue

                        # Extraer procesos CON PAGINATION
                        procesos = self._extraer_con_paginacion(page, "licitacion")

                        # Agregar solo los nuevos
                        nuevos = 0
                        for p in procesos:
                            enlace = p.get('link', '')
                            if enlace and enlace not in enlaces_vistos:
                                procesos_totales.append(p)
                                enlaces_vistos.add(enlace)
                                nuevos += 1
                            elif not enlace:
                                procesos_totales.append(p)
                                nuevos += 1

                        print(f"✓ {nuevos} procesos", flush=True)

                    except Exception as e:
                        print(f"❌", flush=True)
                        continue

                print(f"\n   ✅ Total licitaciones: {len(procesos_totales)}\n")

                # Enriquecer con objeto
                if procesos_totales:
                    self._enriquecer_con_objeto(procesos_totales, browser)

            except Exception as e:
                print(f"   ❌ Error: {e}\n")

            finally:
                browser.close()

        return procesos_totales if procesos_totales else []

    def extraer_compras_menores_completo(self) -> List[Dict[str, Any]]:
        """Extrae TODAS las compras menores por institución CON PAGINATION"""
        print("🔍 Extrayendo compras menores por institución (con pagination)...\n")

        procesos_totales = []
        enlaces_vistos = set()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(30000)

            try:
                for inst_code, (inst_nombre, inst_sigla) in self.institution_map.items():
                    print(f"   🏛️  {inst_sigla}...", end=" ", flush=True)

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

                        # Extraer procesos CON PAGINATION
                        procesos = self._extraer_con_paginacion(page, "compra_menor")

                        # Agregar solo los nuevos
                        nuevos = 0
                        for p in procesos:
                            enlace = p.get('link', '')
                            if enlace and enlace not in enlaces_vistos:
                                procesos_totales.append(p)
                                enlaces_vistos.add(enlace)
                                nuevos += 1
                            elif not enlace:
                                procesos_totales.append(p)
                                nuevos += 1

                        print(f"✓ {nuevos} procesos", flush=True)

                    except Exception as e:
                        print(f"❌", flush=True)
                        continue

                print(f"\n   ✅ Total compras menores: {len(procesos_totales)}\n")

                # Enriquecer con objeto
                if procesos_totales:
                    self._enriquecer_con_objeto(procesos_totales, browser)

            except Exception as e:
                print(f"   ❌ Error: {e}\n")

            finally:
                browser.close()

        return procesos_totales if procesos_totales else []

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

    def _extraer_procesos(self, page, tipo: str = "licitacion") -> List[Dict[str, Any]]:
        """Extrae procesos de la tabla actual (una sola página)"""
        procesos = []
        ahora = datetime.now()

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
        elif "MUNICIPAL" in expediente_clean or "MUNICIPALI" in expediente_clean:
            return "VARIAS MUNICIPALIDADES"
        elif "SPE" in expediente_clean:
            return "VARIAS MUNICIPALIDADES"

        return "VARIAS"


def main():
    extractor = SICCExtractorV11()

    # Extraer licitaciones
    licitaciones = extractor.extraer_licitaciones_completo()

    # Guardar licitaciones
    datos_lic = {
        "metadata": {
            "tipo": "licitaciones",
            "total_procesos": len(licitaciones),
            "inversion_total": 0,
            "moneda": "Lempiras (L.)",
            "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "vigentes",
            "cobertura": "Honduras - Búsqueda por Institución",
            "fuente": "SICC Honduras Compras",
            "metodo_extraccion": "playwright-por-institucion-pagination-v5"
        },
        "procesos": licitaciones
    }

    with open("data/licitaciones.json", "w") as f:
        json.dump(datos_lic, f, indent=2, ensure_ascii=False)

    print(f"✅ Guardado: data/licitaciones.json")

    # Extraer compras menores
    compras_menores = extractor.extraer_compras_menores_completo()

    # Guardar compras menores
    datos_cm = {
        "metadata": {
            "tipo": "compras_menores",
            "total_procesos": len(compras_menores),
            "inversion_total": 0,
            "moneda": "Lempiras (L.)",
            "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "vigentes",
            "cobertura": "Honduras - Búsqueda por Institución",
            "fuente": "SICC Honduras Compras",
            "metodo_extraccion": "playwright-por-institucion-pagination-v5"
        },
        "procesos": compras_menores
    }

    with open("data/compras-menores.json", "w") as f:
        json.dump(datos_cm, f, indent=2, ensure_ascii=False)

    print(f"✅ Guardado: data/compras-menores.json")

    # Resumen
    print(f"""
[──────────────────────────────────────────────────────────]
📋 RESUMEN FINAL
[──────────────────────────────────────────────────────────]
✅ Licitaciones: {len(licitaciones)}
✅ Compras menores: {len(compras_menores)}
✅ Total procesos: {len(licitaciones) + len(compras_menores)}
⏰ Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
============================================================
    """)


if __name__ == "__main__":
    main()
