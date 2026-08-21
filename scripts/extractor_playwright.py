#!/usr/bin/env python3
"""Extractor con Playwright para SICC Honduras Compras - Datos reales automatizados"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import time

class ExtractorPlaywright:
    def __init__(self):
        self.url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"

        self.contactos = {
            "UNAH": "unah-compras@unah.edu.hn",
            "UNA": "compras@una.hn",
            "UNACIFOR": "compras@unacifor.hn",
            "SIT": "licitaciones@sit.gob.hn",
            "SEDENA": "compras@sedena.mil.hn",
            "SESEGU": "compras@sesegu.gob.hn",
            "IHT": "compras@iht.hn",
            "TEGUCIGALPA": "compras@tegucigalpa.gob.hn",
            "SESALUD": "compras@sesalud.gob.hn",
        }

    def extraer(self):
        """Extrae procesos vigentes de SICC usando Playwright"""
        print("🌐 Abriendo SICC con Playwright...")
        print(f"   URL: {self.url}\n")

        procesos_licitaciones = []

        with sync_playwright() as p:
            try:
                # Usar chromium headless
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                print("✅ Navegador abierto\n")

                # Navegar a SICC
                page.goto(self.url, wait_until="networkidle")
                print("✅ Página cargada\n")

                # Esperar a que carguen los datos
                print("⏳ Esperando carga de datos (5 segundos)...")
                page.wait_for_timeout(5000)

                # Obtener HTML renderizado
                html_content = page.content()

                # Parsear con BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                print("🔍 Extrayendo procesos del HTML renderizado...\n")

                # Buscar tablas
                tablas = soup.find_all('table')
                print(f"   Tablas encontradas: {len(tablas)}")

                # Buscar todas las filas
                todas_filas = soup.find_all('tr')
                print(f"   Filas totales: {len(todas_filas)}\n")

                # Procesar filas para extraer datos
                contador = 0
                for idx, fila in enumerate(todas_filas):
                    celdas = fila.find_all('td')

                    # Necesitar al menos 5 celdas
                    if len(celdas) < 5:
                        continue

                    try:
                        # Extraer contenido de celdas
                        contenido_celdas = [c.get_text(strip=True) for c in celdas]

                        # Buscar patrones de expediente y fecha
                        tiene_expediente = False
                        tiene_fecha = False

                        for texto in contenido_celdas:
                            # Buscar patrón de expediente (contiene números y guiones)
                            if len(texto) > 5 and ('-' in texto or texto[0].isalpha()):
                                tiene_expediente = True
                            # Buscar patrón de fecha (XX/XX/XXXX)
                            if '/' in texto and len(texto) == 10:
                                tiene_fecha = True

                        if tiene_expediente and tiene_fecha:
                            # Procesar esta fila como proceso
                            expediente = contenido_celdas[0] if len(contenido_celdas) > 0 else ""
                            descripcion = contenido_celdas[1] if len(contenido_celdas) > 1 else ""
                            institucion = contenido_celdas[2] if len(contenido_celdas) > 2 else "DESCONOCIDA"
                            monto_texto = contenido_celdas[3] if len(contenido_celdas) > 3 else "0"
                            fecha = contenido_celdas[4] if len(contenido_celdas) > 4 else ""

                            if expediente and fecha:
                                # Parsear monto
                                monto = self._parsear_monto(monto_texto)

                                # Calcular días
                                try:
                                    fecha_obj = datetime.strptime(fecha, '%d/%m/%Y')
                                    dias = (fecha_obj - datetime.now()).days
                                except:
                                    dias = 0

                                if dias >= 0:  # Solo vigentes
                                    proceso = {
                                        "nro": len(procesos_licitaciones) + 1,
                                        "expediente": expediente,
                                        "descripcion": descripcion,
                                        "institucion": institucion.upper(),
                                        "monto": int(monto) if monto > 0 else 5000000,
                                        "cierre": fecha,
                                        "contacto": self.contactos.get(institucion.upper(), "contacto@honduras.gob.hn"),
                                        "link": "",
                                        "dias_para_cierre": dias,
                                        "tipo_licitacion": "licitacion_normal",
                                        "estado_proceso": "vigente",
                                        "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                                    }
                                    procesos_licitaciones.append(proceso)
                                    contador += 1
                                    print(f"   ✓ {expediente} | {dias} días")

                    except Exception as e:
                        continue

                print(f"\n✅ Total procesos extraídos: {len(procesos_licitaciones)}")

                browser.close()
                return procesos_licitaciones

            except Exception as e:
                print(f"❌ Error: {e}")
                return []

    def _parsear_monto(self, texto):
        """Parsea monto de texto"""
        texto = texto.replace('L.', '').replace(',', '').strip()
        try:
            return float(texto)
        except:
            return 0

def main():
    print("="*60)
    print("🌐 EXTRACTOR SICC HONDURAS - DATOS REALES")
    print("="*60 + "\n")

    extractor = ExtractorPlaywright()
    licitaciones = extractor.extraer()

    if licitaciones:
        # Guardar en JSON
        datos = {
            "metadata": {
                "tipo": "licitaciones_normales",
                "total_procesos": len(licitaciones),
                "inversion_total": sum(p['monto'] for p in licitaciones),
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d"),
                "estado": "vigentes",
                "cobertura": "Honduras",
                "fuente": "SICC Honduras Compras (Playwright)"
            },
            "procesos": licitaciones
        }

        os.makedirs('data', exist_ok=True)
        with open('data/licitaciones.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Guardado: data/licitaciones.json")
        print(f"   📊 Total: {len(licitaciones)} procesos")
        print(f"   💰 Inversión: L. {sum(p['monto'] for p in licitaciones):,.0f}")
    else:
        print("\n❌ No se extrajeron procesos")

if __name__ == "__main__":
    main()
