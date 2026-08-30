#!/usr/bin/env python3
"""
Extractor UNGM - United Nations Global Marketplace
Extrae procesos de construcción y materiales de UNGM
"""

import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

class ExtractorUNGM:
    """Extrae procesos de construcción de UNGM"""

    def __init__(self):
        self.base_url = "https://www.ungm.org/Public/Notice"
        self.procesos = []

    async def extraer_procesos(self):
        """Extrae procesos de UNGM"""
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                print("⏳ Navegando a UNGM...")
                await page.goto(
                    self.base_url,
                    wait_until='networkidle',
                    timeout=30000
                )

                # Esperar a que carguen los procesos
                await page.wait_for_selector('table tbody tr', timeout=15000)

                print("📊 Extrayendo procesos...")

                # Extraer todas las filas
                rows = await page.query_selector_all('table tbody tr')
                print(f"Found {len(rows)} rows")

                for idx, row in enumerate(rows):
                    try:
                        # Extraer celdas
                        cells = await row.query_selector_all('td')

                        if len(cells) >= 6:
                            referencia = await cells[0].text_content()
                            titulo = await cells[1].text_content()
                            pais = await cells[2].text_content()
                            tipo = await cells[3].text_content()
                            fecha_publicado = await cells[4].text_content()
                            fecha_cierre = await cells[5].text_content()

                            # Intentar obtener link
                            link_elem = await row.query_selector('a')
                            url = ""
                            if link_elem:
                                url = await link_elem.get_attribute('href')
                                if url and not url.startswith('http'):
                                    url = "https://www.ungm.org" + url

                            proceso = {
                                "referencia": referencia.strip(),
                                "titulo": titulo.strip(),
                                "pais": pais.strip(),
                                "tipo": tipo.strip(),
                                "fecha_publicado": fecha_publicado.strip(),
                                "fecha_cierre": fecha_cierre.strip(),
                                "url": url
                            }

                            # Filtrar por tipos relevantes
                            if any(keyword in tipo.lower() for keyword in
                                   ['construcción', 'materiales', 'remodelación',
                                    'construction', 'materials', 'remodeling']):
                                self.procesos.append(proceso)
                                print(f"✅ [{idx+1}] {referencia.strip()[:30]}...")

                    except Exception as e:
                        print(f"⚠️  Error en fila {idx}: {e}")
                        continue

                await browser.close()
                print(f"\n✅ Extracción completada: {len(self.procesos)} procesos encontrados")

            except Exception as e:
                print(f"❌ Error en extracción: {e}")
                print("⚠️  UNGM puede no estar disponible o requiere JavaScript avanzado")
                return False

        return True

    def guardar_datos(self, archivo_salida):
        """Guarda procesos en JSON"""
        datos = {
            "metadata": {
                "fuente": "UNGM - United Nations Global Marketplace",
                "url": self.base_url,
                "tipo": "Procesos de Construcción y Materiales",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d"),
                "total_procesos": len(self.procesos),
                "moneda": "USD / Local",
                "cobertura": "Internacional - Procesos de Construcción"
            },
            "procesos": self.procesos
        }

        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"💾 Datos guardados en: {archivo_salida}")

async def main():
    """Función principal"""
    extractor = ExtractorUNGM()

    if await extractor.extraer_procesos():
        extractor.guardar_datos('data/ungm-construccion.json')
    else:
        print("⚠️  No se pudo completar la extracción automática")
        print("📝 Puede proporcionar los datos manualmente en data/ungm-construccion.json")

if __name__ == '__main__':
    asyncio.run(main())
