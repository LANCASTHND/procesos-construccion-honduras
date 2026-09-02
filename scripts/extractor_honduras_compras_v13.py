#!/usr/bin/env python3
"""
Extractor v13 - Descubrimiento dinámico de IDs + extracción de 16 instituciones
Obtiene automáticamente los IDs desde el dropdown de SICC
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

class SICCExtractorV13:
    """Extractor v13 - Descubrimiento dinámico de IDs"""

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
            "DISTRITO CENTRAL": "compras@distritocental.hn",
            "PRONADERS": "compras@pronaders.hn",
            "SESAL": "compras@sesal.gob.hn",
        }
        # IDs conocidos para instituciones CORE
        self.institution_map = {
            "33": ("Universidad Nacional Autónoma de Honduras (UNAH)", "UNAH"),
            "34": ("Universidad Nacional de Agricultura (UNA)", "UNA"),
            "52": ("Universidad Nacional de Ciencias Forestales (UNACIFOR)", "UNACIFOR"),
            "521": ("Secretaría de Estado en los Despachos de Infraestructura y Transporte (SIT)", "SIT"),
            "20": ("Secretaría de Estado en el Despacho de Defensa Nacional (SEDENA)", "SEDENA"),
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
        self.institution_ids_dynamic = {}

    def _descubrir_ids_dinamicos(self, page):
        """Descubre dinámicamente los IDs de las instituciones desde el dropdown"""
        print("\n🔍 Descubriendo IDs de instituciones desde SICC...")
        
        try:
            page.goto(self.base_url, wait_until='load', timeout=30000)
            time.sleep(1)
            
            # Obtener todas las opciones del dropdown
            opciones = page.query_selector_all('#ctl00_cphCuerpo_wpParametros_ddlEntidades option')
            
            target_institutions = {
                "DISTRITO CENTRAL": None,
                "PRONADERS": None,
                "SESAL": None,
            }
            
            for opcion in opciones:
                try:
                    texto = opcion.text_content().strip()
                    id_val = opcion.get_attribute('value')
                    
                    # Buscar las 3 instituciones nuevas
                    if "DISTRITO CENTRAL" in texto.upper() and id_val:
                        target_institutions["DISTRITO CENTRAL"] = id_val
                        print(f"   ✅ Distrito Central ID: {id_val}")
                    elif "PRONADERS" in texto.upper() and id_val:
                        target_institutions["PRONADERS"] = id_val
                        print(f"   ✅ PRONADERS ID: {id_val}")
                    elif "SESAL" in texto.upper() or "SALUD" in texto.upper():
                        if id_val:
                            target_institutions["SESAL"] = id_val
                            print(f"   ✅ SESAL ID: {id_val}")
                            
                except:
                    continue
            
            # Agregar los IDs descubiertos al mapa
            for inst_name, id_val in target_institutions.items():
                if id_val:
                    self.institution_map[id_val] = (f"Institución: {inst_name}", inst_name)
                    self.institution_ids_dynamic[inst_name] = id_val
                else:
                    print(f"   ⚠️  No encontrado: {inst_name}")
                    
        except Exception as e:
            print(f"   ❌ Error descubriendo IDs: {e}")

    def _extraer_con_paginacion(self, page, tipo: str = "licitacion") -> List[Dict[str, Any]]:
        """Extrae procesos manejando TODAS las páginas de resultados"""
        procesos_totales = []
        pagina_actual = 1

        while True:
            print(f"      📄 Página {pagina_actual}...", end=" ", flush=True)

            try:
                filas = page.query_selector_all('table[id*="gvResultados"] tbody tr')
                if not filas:
                    print("vacía", flush=True)
                    break

                procesos_pagina = []
                for fila in filas:
                    try:
                        celdas = fila.query_selector_all('td')
                        if len(celdas) < 8:
                            continue

                        expediente = celdas[1].text_content().strip()
                        descripcion = celdas[2].text_content().strip()
                        modalidad = celdas[3].text_content().strip()
                        etapa = celdas[4].text_content().strip()
                        cierre_text = celdas[5].text_content().strip()
                        monto_text = celdas[6].text_content().strip()

                        try:
                            fecha_cierre = datetime.strptime(cierre_text, "%d/%m/%Y")
                            if fecha_cierre.year < 2026 or fecha_cierre < datetime.now():
                                continue
                        except:
                            continue

                        dias = (fecha_cierre - datetime.now()).days
                        monto = 0
                        try:
                            monto = int(''.join(filter(str.isdigit, monto_text)))
                        except:
                            pass

                        link_elem = celdas[0].query_selector('a')
                        link = link_elem.get_attribute('href') if link_elem else ""

                        proceso = {
                            "expediente": expediente,
                            "descripcion": descripcion,
                            "modalidad": modalidad,
                            "etapa": etapa,
                            "cierre": cierre_text,
                            "monto": monto,
                            "dias_para_cierre": dias,
                            "tipo_licitacion": tipo,
                            "link": link,
                            "estado_proceso": "vigente",
                            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                        }

                        procesos_pagina.append(proceso)

                    except Exception:
                        continue

                procesos_totales.extend(procesos_pagina)
                print(f"✓ {len(procesos_pagina)}", flush=True)

                # Siguiente página
                try:
                    btn = page.query_selector('a[id*="lnkSiguiente"]')
                    if not btn or 'disabled' in btn.get_attribute('class', ''):
                        break

                    btn.click()
                    time.sleep(1)
                    pagina_actual += 1

                except:
                    break

            except Exception as e:
                print(f"error", flush=True)
                break

        return procesos_totales

    def extraer_licitaciones_completo(self) -> List[Dict[str, Any]]:
        """Extrae licitaciones de todas las instituciones"""
        print("🔍 Extrayendo licitaciones por institución (con pagination)...\n")

        procesos_totales = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(30000)

            try:
                # Descubrir IDs dinámicamente
                self._descubrir_ids_dinamicos(page)
                
                for inst_code, (inst_nombre, inst_sigla) in self.institution_map.items():
                    print(f"   🏛️  {inst_sigla}...", end=" ", flush=True)

                    try:
                        page.goto(self.base_url, wait_until='load')
                        time.sleep(0.5)

                        # Seleccionar institución
                        try:
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlEntidades', inst_code)
                        except:
                            print("❌", flush=True)
                            continue

                        time.sleep(0.5)

                        # Seleccionar licitación
                        try:
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipos', 'licitacion')
                        except:
                            pass

                        time.sleep(0.5)

                        # Buscar
                        try:
                            page.click('#ctl00_cphCuerpo_wpParametros_btnBuscar')
                        except:
                            pass

                        time.sleep(1)

                        # Extraer procesos
                        procesos = self._extraer_con_paginacion(page, "licitacion")

                        for proc in procesos:
                            proc['institucion'] = inst_sigla
                            proc['contacto'] = self.contactos.get(inst_sigla, "no-disponible@hnd.gob.hn")

                        procesos_totales.extend(procesos)
                        print(f"✓ ({len(procesos)} procesos)")

                    except Exception as e:
                        print(f"✗ ({str(e)[:30]})")
                        continue

            finally:
                browser.close()

        return procesos_totales

    def extraer_compras_menores_completo(self) -> List[Dict[str, Any]]:
        """Extrae compras menores de todas las instituciones"""
        print("\n🔍 Extrayendo compras menores por institución (con pagination)...\n")

        procesos_totales = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(30000)

            try:
                for inst_code, (inst_nombre, inst_sigla) in self.institution_map.items():
                    print(f"   🏛️  {inst_sigla}...", end=" ", flush=True)

                    try:
                        page.goto(self.base_url, wait_until='load')
                        time.sleep(0.5)

                        # Seleccionar institución
                        try:
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlEntidades', inst_code)
                        except:
                            print("❌", flush=True)
                            continue

                        time.sleep(0.5)

                        # Seleccionar compra menor
                        try:
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipos', 'compra_menor')
                        except:
                            pass

                        time.sleep(0.5)

                        # Buscar
                        try:
                            page.click('#ctl00_cphCuerpo_wpParametros_btnBuscar')
                        except:
                            pass

                        time.sleep(1)

                        # Extraer procesos
                        procesos = self._extraer_con_paginacion(page, "compra_menor")

                        for proc in procesos:
                            proc['institucion'] = inst_sigla
                            proc['contacto'] = self.contactos.get(inst_sigla, "no-disponible@hnd.gob.hn")

                        procesos_totales.extend(procesos)
                        print(f"✓ ({len(procesos)} procesos)")

                    except Exception as e:
                        print(f"✗ ({str(e)[:30]})")
                        continue

            finally:
                browser.close()

        return procesos_totales

    def _eliminar_duplicados(self, procesos: List) -> List:
        """Elimina duplicados por expediente"""
        vistos = set()
        unicos = []
        for p in procesos:
            exp = p.get('expediente', '').strip()
            if exp and exp not in vistos:
                vistos.add(exp)
                unicos.append(p)
        return unicos

    def consolidar_y_guardar(self, licitaciones, compras_menores):
        """Consolida y guarda datos finales"""
        print("\n" + "="*70)
        print("CONSOLIDANDO DATOS")
        print("="*70 + "\n")

        licitaciones = self._eliminar_duplicados(licitaciones)
        compras_menores = self._eliminar_duplicados(compras_menores)

        licitaciones.sort(key=lambda x: x.get('cierre', ''), reverse=True)
        compras_menores.sort(key=lambda x: x.get('cierre', ''), reverse=True)

        datos_lic = {
            "metadata": {
                "tipo": "licitaciones",
                "total_procesos": len(licitaciones),
                "inversion_total": sum(p.get('monto', 0) for p in licitaciones),
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "vigentes",
                "cobertura": "Honduras - 16 Instituciones (Dinámico)",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "playwright-v13-discovery",
            },
            "procesos": licitaciones
        }

        datos_cm = {
            "metadata": {
                "tipo": "compras_menores",
                "total_procesos": len(compras_menores),
                "inversion_total": sum(p.get('monto', 0) for p in compras_menores),
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "vigentes",
                "cobertura": "Honduras - 16 Instituciones (Dinámico)",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "playwright-v13-discovery",
            },
            "procesos": compras_menores
        }

        with open('data/licitaciones.json', 'w', encoding='utf-8') as f:
            json.dump(datos_lic, f, indent=2, ensure_ascii=False)

        with open('data/compras-menores.json', 'w', encoding='utf-8') as f:
            json.dump(datos_cm, f, indent=2, ensure_ascii=False)

        print(f"✅ Licitaciones: {len(licitaciones)}")
        print(f"✅ Compras menores: {len(compras_menores)}")
        print(f"✅ Total: {len(licitaciones) + len(compras_menores)} vigentes\n")


if __name__ == "__main__":
    extractor = SICCExtractorV13()
    licitaciones = extractor.extraer_licitaciones_completo()
    compras_menores = extractor.extraer_compras_menores_completo()
    extractor.consolidar_y_guardar(licitaciones, compras_menores)
    sys.exit(0)
