#!/usr/bin/env python3
"""
Extractor v9 - Selectivo: 14 CORE + 2 NUEVAS + varían según actividad
Procesa solo instituciones confirmadas con actividad
"""

import json
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Error: pip install playwright")
    sys.exit(1)

class SICCExtractorV9:
    """Extractor v9 - Selectivo (instituciones confirmadas)"""

    def __init__(self):
        self.base_url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"

        # Instituciones CORE (14)
        self.instituciones_core = {
            "UNAH": {"name": "Universidad Nacional Autónoma de Honduras (UNAH)", "contact": "unah-compras@unah.edu.hn"},
            "UNA": {"name": "Universidad Nacional de Agricultura (UNA)", "contact": "compras@una.hn"},
            "UNACIFOR": {"name": "Universidad Nacional de Ciencias Forestales (UNACIFOR)", "contact": "compras@unacifor.hn"},
            "SIT": {"name": "Secretaría de Estado en los Despachos de Infraestructura y Transporte (SIT)", "contact": "licitaciones@sit.gob.hn"},
            "SEDENA": {"name": "Secretaría de Estado en los Despachos de Defensa (SEDENA)", "contact": "compras@sedena.mil.hn"},
            "SESEGU": {"name": "Secretaría de Seguridad (SESEGU)", "contact": "compras@sesegu.gob.hn"},
            "IHT": {"name": "Instituto Hondureño de Turismo (IHT)", "contact": "compras@iht.hn"},
            "TEGUCIGALPA": {"name": "Municipalidad de Tegucigalpa", "contact": "compras@tegucigalpa.gob.hn"},
            "SAN PEDRO SULA": {"name": "Municipalidad de San Pedro Sula", "contact": "compras@sanpedrosula.gob.hn"},
            "LA CEIBA": {"name": "Municipalidad de La Ceiba", "contact": "compras@laceiba.gob.hn"},
            "DANLI": {"name": "Municipalidad de Danlí", "contact": "compras@danli.gob.hn"},
            "EL RAMA": {"name": "Municipalidad de El Rama", "contact": "compras@elrama.gob.hn"},
            "COMAYAGUA": {"name": "Municipalidad de Comayagua", "contact": "compras@comayagua.gob.hn"},
            "CHOLOMA": {"name": "Municipalidad de Choloma", "contact": "compras@munichol.hn"},
        }

        # Instituciones NUEVAS (2)
        self.instituciones_nuevas = {
            "DISTRITO CENTRAL": {"name": "Municipalidad del Distrito Central", "contact": "compras@distritocental.hn"},
            "PRONADERS": {"name": "PRONADERS", "contact": "compras@pronaders.hn"},
        }

        self.palabras_construccion = [
            'construcción', 'obra', 'remodelación', 'ingeniería', 'supervisión',
            'pavimentación', 'infraestructura', 'mejoramiento', 'edificio', 'vial',
            'carretera', 'puente', 'drenaje', 'alcantarillado', 'agua potable',
            'servicios de ingeniería', 'diseño', 'ampliación', 'renovación', 'mantenimiento'
        ]

    def _es_construccion(self, texto: str) -> bool:
        """Verifica construcción/ingeniería"""
        texto_lower = texto.lower()
        return any(palabra in texto_lower for palabra in self.palabras_construccion)

    def _encontrar_institucion_id(self, page, nombre_inst: str) -> str:
        """Busca el ID de institución en dropdown"""
        try:
            opciones = page.query_selector_all('#ctl00_cphCuerpo_wpParametros_ddlEntidades option')
            for opcion in opciones:
                try:
                    if nombre_inst.lower() in opcion.text_content().lower():
                        return opcion.get_attribute('value')
                except:
                    continue
        except:
            pass
        return None

    def _extraer_procesos_institucion(self, page, tipo: str, ahora: datetime) -> List[Dict]:
        """Extrae procesos de la institución actual"""
        procesos = []
        pagina = 1

        while pagina <= 30:
            try:
                filas = page.query_selector_all('table[id*="gvResultados"] tbody tr')
                if not filas:
                    break

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

                        # Filtrar construcción
                        if not self._es_construccion(f"{expediente} {descripcion} {modalidad}"):
                            continue

                        # Filtrar fecha
                        try:
                            fecha_cierre = datetime.strptime(cierre_text, "%d/%m/%Y")
                            if fecha_cierre.year < 2026 or fecha_cierre < ahora:
                                continue
                        except:
                            continue

                        dias = (fecha_cierre - ahora).days

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

                        procesos.append(proceso)

                    except Exception:
                        continue

                # Siguiente página
                try:
                    btn = page.query_selector('a[id*="lnkSiguiente"]')
                    if not btn or 'disabled' in btn.get_attribute('class', ''):
                        break

                    btn.click()
                    time.sleep(0.3)
                    pagina += 1

                except:
                    break

            except Exception:
                break

        return procesos

    def extraer(self):
        """Extrae de todas las instituciones configuradas"""
        print("\n" + "="*70)
        print("EXTRACTOR v9 - SELECTIVO (CORE + NUEVAS)")
        print("="*70 + "\n")

        todas_instituciones = {**self.instituciones_core, **self.instituciones_nuevas}
        print(f"🏢 Instituciones a procesar: {len(todas_instituciones)}\n")

        licitaciones = []
        compras_menores = []
        ahora = datetime.now()
        fallidas = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(30000)

                for idx, (codigo, info) in enumerate(todas_instituciones.items(), 1):
                    try:
                        print(f"   {idx:2d}. {codigo:15s}", end=" ", flush=True)

                        # Navegar
                        page.goto(self.base_url, wait_until='load', timeout=30000)
                        time.sleep(0.3)

                        # Encontrar ID
                        inst_id = self._encontrar_institucion_id(page, codigo)
                        if not inst_id:
                            print("✗ (no encontrada)")
                            fallidas.append(codigo)
                            continue

                        # Licitaciones
                        procs_lic = []
                        try:
                            page.goto(self.base_url, wait_until='load', timeout=30000)
                            time.sleep(0.3)
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlEntidades', inst_id)
                            time.sleep(0.5)
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipos', 'licitacion')
                            time.sleep(0.5)

                            procs_lic = self._extraer_procesos_institucion(page, "licitacion", ahora)

                            for proc in procs_lic:
                                proc['institucion'] = codigo
                                proc['contacto'] = info['contact']
                                licitaciones.append(proc)

                        except Exception as e:
                            pass

                        # Compras menores
                        procs_cm = []
                        try:
                            page.goto(self.base_url, wait_until='load', timeout=30000)
                            time.sleep(0.3)
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlEntidades', inst_id)
                            time.sleep(0.5)
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipos', 'compra_menor')
                            time.sleep(0.5)

                            procs_cm = self._extraer_procesos_institucion(page, "compra_menor", ahora)

                            for proc in procs_cm:
                                proc['institucion'] = codigo
                                proc['contacto'] = info['contact']
                                compras_menores.append(proc)

                        except Exception as e:
                            pass

                        print(f"✓ ({len(procs_lic)}L + {len(procs_cm)}C)")

                    except Exception as e:
                        print(f"✗ ({str(e)[:30]})")
                        fallidas.append(codigo)
                        continue

                browser.close()

        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False

        # Consolidar
        self._consolidar(licitaciones, compras_menores, fallidas)
        return True

    def _consolidar(self, licitaciones: List, compras_menores: List, fallidas: List):
        """Consolida datos finales"""
        print("\n" + "="*70)
        print("CONSOLIDANDO")
        print("="*70 + "\n")

        # Eliminar duplicados
        licitaciones = self._eliminar_duplicados(licitaciones)
        compras_menores = self._eliminar_duplicados(compras_menores)

        # Ordenar
        licitaciones.sort(key=lambda x: x.get('cierre', ''), reverse=True)
        compras_menores.sort(key=lambda x: x.get('cierre', ''), reverse=True)

        # Guardar JSON
        datos_lic = {
            "metadata": {
                "tipo": "licitaciones",
                "total_procesos": len(licitaciones),
                "inversion_total": sum(p.get('monto', 0) for p in licitaciones),
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "vigentes",
                "cobertura": "Honduras - 16 Instituciones (Core + Nuevas)",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "playwright-selectivo-v9",
                "instituciones_procesadas": 16 - len(fallidas),
                "instituciones_fallidas": len(fallidas)
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
                "cobertura": "Honduras - 16 Instituciones (Core + Nuevas)",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "playwright-selectivo-v9",
                "instituciones_procesadas": 16 - len(fallidas),
                "instituciones_fallidas": len(fallidas)
            },
            "procesos": compras_menores
        }

        with open('data/licitaciones.json', 'w', encoding='utf-8') as f:
            json.dump(datos_lic, f, indent=2, ensure_ascii=False)

        with open('data/compras-menores.json', 'w', encoding='utf-8') as f:
            json.dump(datos_cm, f, indent=2, ensure_ascii=False)

        print(f"✅ Licitaciones: {len(licitaciones)} procesos")
        print(f"✅ Compras menores: {len(compras_menores)} procesos")
        print(f"✅ Total: {len(licitaciones) + len(compras_menores)} vigentes\n")

    def _eliminar_duplicados(self, procesos: List) -> List:
        """Elimina duplicados"""
        vistos = set()
        unicos = []
        for p in procesos:
            exp = p.get('expediente', '').strip()
            if exp and exp not in vistos:
                vistos.add(exp)
                unicos.append(p)
        return unicos


if __name__ == "__main__":
    extractor = SICCExtractorV9()
    exito = extractor.extraer()
    sys.exit(0 if exito else 1)
