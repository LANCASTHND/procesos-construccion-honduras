#!/usr/bin/env python3
"""
Extractor v4 - Búsqueda por institución para capturar TODOS los procesos
Optimizado para velocidad y completitud
"""

import json
import sys
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Error: pip install playwright")
    sys.exit(1)

class SICCExtractorV4:
    """Extractor v4 - Búsqueda por institución"""

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
        }
        # Mapeo de códigos SICC a instituciones
        self.institution_map = {
            "33": ("Universidad Nacional Autónoma de Honduras (UNAH)", "UNAH"),
            "34": ("Universidad Nacional de Agricultura (UNA)", "UNA"),
            "52": ("Universidad Nacional de Ciencias Forestales (UNACIFOR)", "UNACIFOR"),
            "521": ("Secretaría de Estado en los Despachos de Infraestructura y Transporte (SIT)", "SIT"),
            "20": ("Secretaría de Estado en el Despacho de Defensa Nacional SEDENA)", "SEDENA"),
            "40": ("Secretaría de Estado en el Despacho de Seguridad (SESEGU)", "SESEGU"),
            "493": ("Instituto Hondureño de Turismo (IHT)", "IHT"),
            "103": ("Municipalidad de Tegucigalpa", "TEGUCIGALPA"),
            "106": ("Municipalidad de San Pedro Sula, Cortés", "SAN PEDRO SULA"),
            "107": ("Municipalidad de La Ceiba, Atlantida", "LA CEIBA"),
            "185": ("Municipalidad de Danli, El Paraíso", "DANLI"),
            "102": ("Municipalidad de Comayagua, Comayagua", "COMAYAGUA"),
            "151": ("Municipalidad de Choloma, Cortés", "CHOLOMA"),
            "405": ("Cuerpo de Bomberos de Honduras (CBH)", "CUERPO DE BOMBEROS"),
        }

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

    def _enriquecer_con_objeto(self, procesos: List[Dict], browser) -> None:
        """Enriquece procesos vigentes con objeto (descripción detallada)"""
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
                if i % 10 == 0:
                    print(f"      ✓ {i}/{len(vigentes)} procesados ({contador} descripciones)...")
            except:
                pass

            time.sleep(0.2)

        print(f"      ✓ {contador}/{len(vigentes)} descripciones extraídas\n")

    def extraer_licitaciones_completo(self) -> List[Dict[str, Any]]:
        """Extrae TODAS las licitaciones por institución"""
        print("🔍 Extrayendo licitaciones por institución...\n")

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

                        # Extraer procesos
                        procesos = self._extraer_procesos(page, "licitacion")

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

                        print(f"✓ {nuevos}", flush=True)

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
        """Extrae TODAS las compras menores por institución"""
        print("🔍 Extrayendo compras menores por institución...\n")

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

                        # Extraer procesos
                        procesos = self._extraer_procesos(page, "compra_menor")

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

                        print(f"✓ {nuevos}", flush=True)

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

    def _extraer_objeto(self, browser, link: str) -> str:
        """Extrae el objeto (descripción detallada del proyecto) de la página de detalle"""
        detail_page = None
        try:
            if not link:
                return ""

            # Construir URL completa si es relativa
            if link.startswith('/'):
                url = "http://sicc.honducompras.gob.hn" + link
            elif not link.startswith('http'):
                url = "http://sicc.honducompras.gob.hn/HC/procesos/" + link
            else:
                url = link

            # Crear nueva página
            detail_page = browser.new_page()
            detail_page.set_default_timeout(10000)

            detail_page.goto(url, wait_until='domcontentloaded', timeout=10000)
            time.sleep(0.3)

            # Buscar "Objeto" o "Proyecto" en la tabla
            try:
                filas = detail_page.query_selector_all('table tr')
                for fila in filas:
                    celdas = fila.query_selector_all('td')
                    if len(celdas) >= 2:
                        label = celdas[0].text_content().strip().lower()
                        if 'objeto' in label:
                            objeto = celdas[1].text_content().strip()
                            if objeto and len(objeto) > 10:
                                return objeto[:280]
            except:
                pass

            return ""
        except:
            return ""
        finally:
            if detail_page:
                try:
                    detail_page.close()
                except:
                    pass

    def _extraer_procesos(self, page, tipo: str = "licitacion") -> List[Dict[str, Any]]:
        """Extrae procesos de la tabla actual"""
        procesos = []

        try:
            # Esperar contexto
            for i in range(5):
                try:
                    time.sleep(0.5)
                    page.query_selector('body')
                    break
                except:
                    if i == 4:
                        return procesos

            # Encontrar tabla
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

            # Extraer filas
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

                    # Extraer fecha
                    fecha_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', vigencia_texto)
                    if not fecha_match:
                        continue

                    fecha_inicio_str = fecha_match.group(0)

                    try:
                        fecha_inicio = datetime.strptime(fecha_inicio_str, '%d/%m/%Y')
                        cierre_estimado = fecha_inicio + timedelta(days=35)
                        dias = (cierre_estimado - datetime.now()).days

                        if dias < -90:
                            continue
                    except:
                        continue

                    institucion = self._extraer_institucion(expediente)

                    proceso = {
                        "expediente": expediente[:80],
                        "descripcion": modalidad,
                        "institucion": institucion,
                        "monto": 0,
                        "cierre": cierre_estimado.strftime('%d/%m/%Y'),
                        "contacto": self.contactos.get(institucion, ""),
                        "link": link,
                        "dias_para_cierre": dias,
                        "tipo_licitacion": tipo,
                        "etapa": etapa,
                        "modalidad": modalidad,
                        "fecha_inicio": fecha_inicio_str,
                        "objeto": "",
                        "estado_proceso": "vigente" if dias >= 0 else "próximo_cierre",
                        "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                    }
                    procesos.append(proceso)

                except Exception as e:
                    continue

        except Exception as e:
            pass

        return procesos

    def guardar_json(self, procesos: List[Dict], tipo: str, archivo: str):
        """Guarda procesos en JSON"""
        total = len(procesos)
        inversion_total = sum(p.get('monto', 0) for p in procesos)

        for idx, proceso in enumerate(procesos, 1):
            if 'nro' not in proceso:
                proceso['nro'] = idx

        datos = {
            "metadata": {
                "tipo": "licitaciones_normales" if tipo == "licitaciones" else "compras_menores",
                "total_procesos": total,
                "inversion_total": inversion_total,
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "vigentes",
                "cobertura": "Honduras - Búsqueda por Institución",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "playwright-por-institucion-completo"
            },
            "procesos": procesos
        }

        os.makedirs(os.path.dirname(archivo) if os.path.dirname(archivo) else '.', exist_ok=True)

        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"✅ Guardado: {archivo}")
        print(f"   📊 Total: {total} procesos\n")

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🏗️  EXTRACTOR HONDURAS COMPRAS v4 (Búsqueda por Institución)")
    print("="*60 + "\n")

    extractor = SICCExtractorV4()
    os.makedirs('data', exist_ok=True)

    print("["+"─"*58+"]")
    print("LICITACIONES (BÚSQUEDA COMPLETA)")
    print("["+"─"*58+"]\n")
    licitaciones = extractor.extraer_licitaciones_completo()
    extractor.guardar_json(licitaciones, "licitaciones", "data/licitaciones.json")

    print("["+"─"*58+"]")
    print("COMPRAS MENORES (BÚSQUEDA COMPLETA)")
    print("["+"─"*58+"]\n")
    compras_menores = extractor.extraer_compras_menores_completo()
    extractor.guardar_json(compras_menores, "compras_menores", "data/compras-menores.json")

    print("["+"─"*58+"]")
    print("📋 RESUMEN FINAL")
    print("["+"─"*58+"]")
    print(f"✅ Licitaciones: {len(licitaciones)}")
    print(f"✅ Compras menores: {len(compras_menores)}")
    print(f"✅ Total procesos: {len(licitaciones) + len(compras_menores)}")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
