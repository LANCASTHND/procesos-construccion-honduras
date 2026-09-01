#!/usr/bin/env python3
"""
Extractor v10 - Robusto: Evita dropdown lento con búsqueda global
Hace una búsqueda global sin filtro institución, extrae todos y filtra en Python
"""

import json
import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Set

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Error: pip install playwright")
    sys.exit(1)

class SICCExtractorV10:
    """Extractor v10 - Búsqueda global, sin dropdown"""

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
            "CUERPO DE BOMBEROS": "compras@cuerpodbomberos.hn",
            "TEGUCIGALPA": "compras@tegucigalpa.gob.hn",
            "SAN PEDRO SULA": "compras@sanpedrosula.gob.hn",
            "LA CEIBA": "compras@laceiba.gob.hn",
            "DANLI": "compras@danli.gob.hn",
            "EL RAMA": "compras@elrama.gob.hn",
            "COMAYAGUA": "compras@comayagua.gob.hn",
            "CHOLOMA": "compras@munichol.hn",
            "DISTRITO CENTRAL": "compras@distritocental.hn",
            "PRONADERS": "compras@pronaders.hn",
        }
        self.palabras_construccion = [
            'construcción', 'obra', 'remodelación', 'ingeniería', 'supervisión',
            'pavimentación', 'infraestructura', 'mejoramiento', 'edificio', 'vial',
            'carretera', 'puente', 'drenaje', 'alcantarillado', 'agua potable',
            'servicios de ingeniería', 'diseño', 'ampliación', 'renovación', 'mantenimiento'
        ]

    def _es_construccion(self, texto: str) -> bool:
        """Verifica si es construcción/ingeniería"""
        texto_lower = texto.lower()
        return any(palabra in texto_lower for palabra in self.palabras_construccion)

    def _extraer_paginas(self, page, tipo: str, ahora: datetime) -> List[Dict]:
        """Extrae procesos de todas las páginas (búsqueda global)"""
        procesos = []
        pagina = 1

        print(f"\n   Extrayendo {tipo}s...")

        while pagina <= 50:
            try:
                filas = page.query_selector_all('table[id*="gvResultados"] tbody tr')
                if not filas:
                    if pagina == 1:
                        print("      ⚠️  No hay resultados")
                    break

                print(f"      📄 Página {pagina}: {len(filas)} registros", end="")

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
                        institucion_raw = celdas[7].text_content().strip() if len(celdas) > 7 else ""

                        # Filtrar construcción
                        if not self._es_construccion(f"{expediente} {descripcion} {modalidad}"):
                            continue

                        # Filtrar fecha 2026+
                        try:
                            fecha_cierre = datetime.strptime(cierre_text, "%d/%m/%Y")
                            if fecha_cierre.year < 2026 or fecha_cierre < ahora:
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

                        # Extraer institución
                        institucion = institucion_raw.split('-')[0].strip() if '-' in institucion_raw else institucion_raw.strip()

                        proceso = {
                            "expediente": expediente,
                            "descripcion": descripcion,
                            "institucion": institucion,
                            "modalidad": modalidad,
                            "etapa": etapa,
                            "cierre": cierre_text,
                            "monto": monto,
                            "dias_para_cierre": dias,
                            "tipo_licitacion": tipo,
                            "link": link,
                            "contacto": self.contactos.get(institucion.split()[0].upper(), "no-disponible@hnd.gob.hn"),
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

        return procesos

    def extraer(self):
        """Extrae con búsqueda global, sin dropdown lento"""
        print("\n" + "="*70)
        print("EXTRACTOR v10 - ROBUSTO (búsqueda global, sin dropdown)")
        print("="*70 + "\n")

        ahora = datetime.now()

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(30000)

                # Licitaciones globales
                print("🔍 BÚSQUEDA GLOBAL LICITACIONES")
                page.goto(self.base_url, wait_until='load', timeout=30000)
                time.sleep(0.5)

                licitaciones = self._extraer_paginas(page, "licitacion", ahora)

                # Compras menores globales
                print("\n🔍 BÚSQUEDA GLOBAL COMPRAS MENORES")
                page.goto(self.base_url, wait_until='load', timeout=30000)
                time.sleep(0.5)

                # NO seleccionar tipo, dejar por defecto = busca ambas?
                # O buscar compras menores específicamente
                try:
                    page.click('input[id*="rdoCompMenor"]', timeout=5000)
                    time.sleep(1)
                except:
                    pass

                compras_menores = self._extraer_paginas(page, "compra_menor", ahora)

                browser.close()

                self._consolidar(licitaciones, compras_menores)
                return True

        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False

    def _consolidar(self, licitaciones: List, compras_menores: List):
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
                "cobertura": "Honduras - Búsqueda Global",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "playwright-busqueda-global-v10",
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
                "cobertura": "Honduras - Búsqueda Global",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "playwright-busqueda-global-v10",
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
    extractor = SICCExtractorV10()
    exito = extractor.extraer()
    sys.exit(0 if exito else 1)
