#!/usr/bin/env python3
"""
Extractor avanzado de SICC Honduras con búsqueda por institución
Usa Playwright para manejar JavaScript y formularios ASP.NET
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import time

try:
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Instala: pip install playwright beautifulsoup4")
    print("   Luego: playwright install chromium")
    exit(1)

class SICCAvanzadoExtractor:
    """Extractor de SICC con navegador Playwright"""

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
        }
        self.instituciones = list(self.contactos.keys())

    def extraer_por_institucion(self, institucion: str) -> List[Dict[str, Any]]:
        """Extrae procesos de una institución usando Playwright"""
        procesos = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Acceder a la página
                page.goto(self.base_url, timeout=30000)
                time.sleep(2)

                # Esperar a que cargue el dropdown de instituciones
                try:
                    dropdown = page.locator("select[id*='ddlInstitucion']").first
                    if dropdown:
                        dropdown.select_option(institucion)
                        time.sleep(1)
                except:
                    pass

                # Hacer click en buscar
                try:
                    search_btn = page.locator("input[type='submit'][value*='Buscar']").first
                    if search_btn:
                        search_btn.click()
                        page.wait_for_load_state("networkidle")
                        time.sleep(2)
                except:
                    pass

                # Obtener HTML y parsear
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')

                # Buscar tablas de resultados
                tablas = soup.find_all('table')

                for tabla in tablas:
                    filas = tabla.find_all('tr')
                    if len(filas) < 2:
                        continue

                    for fila in filas[1:]:
                        celdas = fila.find_all('td')
                        if len(celdas) < 5:
                            continue

                        try:
                            expediente = celdas[0].text.strip()
                            descripcion = celdas[1].text.strip()
                            inst_text = celdas[2].text.strip().upper()
                            monto_text = celdas[3].text.strip()
                            fecha_cierre = celdas[4].text.strip()

                            if not expediente or not fecha_cierre:
                                continue

                            # Parsear monto
                            monto_clean = monto_text.replace('L.', '').replace(',', '').strip()
                            try:
                                monto = float(monto_clean) if monto_clean else 0
                            except:
                                monto = 0

                            # Calcular días para cierre
                            try:
                                from datetime import datetime
                                cierre_date = datetime.strptime(fecha_cierre, '%d/%m/%Y')
                                hoy = datetime.now()
                                dias = (cierre_date - hoy).days
                            except:
                                continue

                            if dias > 0:  # Solo vigentes
                                proceso = {
                                    "expediente": expediente,
                                    "descripcion": descripcion,
                                    "institucion": inst_text,
                                    "monto": monto if monto > 0 else 5000000,
                                    "cierre": fecha_cierre,
                                    "contacto": self.contactos.get(inst_text, "contacto@honduras.gob.hn"),
                                    "link": "",
                                    "dias_para_cierre": dias,
                                    "tipo_licitacion": "licitacion_normal",
                                    "estado_proceso": "vigente",
                                    "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                                }

                                # Buscar link en la fila
                                for celda in celdas:
                                    link_elem = celda.find('a')
                                    if link_elem and link_elem.get('href'):
                                        proceso['link'] = link_elem.get('href', '')
                                        break

                                procesos.append(proceso)

                        except Exception as e:
                            continue

                browser.close()

        except Exception as e:
            print(f"      ❌ Error con Playwright: {e}")

        return procesos

    def extraer_licitaciones(self) -> List[Dict[str, Any]]:
        """Extrae licitaciones por institución"""
        print("🔍 Extrayendo licitaciones por institución (Playwright)...\n")

        procesos_totales = []

        for institucion in self.instituciones:
            print(f"   🏢 {institucion}...", end=" ")
            procesos = self.extraer_por_institucion(institucion)

            if procesos:
                procesos_totales.extend(procesos)
                print(f"✅ {len(procesos)}")
            else:
                print("⚠️  Sin procesos")

        print(f"\n   Total: {len(procesos_totales)} procesos\n")
        return procesos_totales

    def guardar_json(self, procesos: List[Dict], tipo: str):
        """Guarda en JSON"""
        total = len(procesos)
        inversion = sum(p.get('monto', 0) for p in procesos)

        for idx, p in enumerate(procesos, 1):
            if 'nro' not in p:
                p['nro'] = idx

        datos = {
            "metadata": {
                "tipo": "licitaciones_normales" if tipo == "lic" else "compras_menores",
                "total_procesos": total,
                "inversion_total": inversion,
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d"),
                "estado": "vigentes",
                "cobertura": "Honduras",
                "fuente": "SICC Honduras Compras"
            },
            "procesos": procesos
        }

        archivo = "data/licitaciones.json" if tipo == "lic" else "data/compras-menores.json"
        os.makedirs('data', exist_ok=True)

        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"✅ Guardado: {archivo}")
        print(f"   📊 Total: {total} | 💰 Inversión: L. {inversion:,.0f}")

def main():
    print("\n" + "="*60)
    print("🏗️  EXTRACTOR SICC AVANZADO - BÚSQUEDA POR INSTITUCIÓN")
    print("="*60 + "\n")

    extractor = SICCAvanzadoExtractor()

    licitaciones = extractor.extraer_licitaciones()
    extractor.guardar_json(licitaciones, "lic")

    print("\n" + "="*60)
    print(f"✅ Extracción completada: {len(licitaciones)} procesos")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
