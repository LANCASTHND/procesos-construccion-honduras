#!/usr/bin/env python3
"""
Extractor UNGM v2 - Con soporte para filtros
Extrae procesos de construcción y materiales de UNGM para Honduras
"""

import json
import asyncio
import time
from datetime import datetime
from playwright.async_api import async_playwright

class ExtractorUNGMv2:
    """Extrae procesos de UNGM con filtros aplicados"""

    def __init__(self):
        self.base_url = "https://www.ungm.org/Public/Notice"
        self.procesos = []

    async def extraer_procesos(self):
        """Extrae procesos con filtros de construcción y Honduras"""
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Configurar timeout más largo
                page.set_default_timeout(60000)
                page.set_default_navigation_timeout(60000)

                print("⏳ Navegando a UNGM...")
                await page.goto(
                    self.base_url,
                    wait_until='domcontentloaded',
                    timeout=60000
                )

                print("⏳ Esperando carga de página...")
                await asyncio.sleep(3)

                # Buscar y mostrar elementos disponibles
                print("🔍 Inspeccionando página...")
                
                # Intentar buscar filtros
                search_fields = await page.query_selector_all('input[type="text"], input[placeholder*="search"], input[placeholder*="Search"]')
                print(f"   Campos de búsqueda encontrados: {len(search_fields)}")

                selects = await page.query_selector_all('select')
                print(f"   Campos select encontrados: {len(selects)}")

                # Buscar tabla de datos
                tables = await page.query_selector_all('table')
                print(f"   Tablas encontradas: {len(tables)}")

                if len(tables) > 0:
                    print("📊 Extrayendo datos de tabla...")
                    rows = await tables[0].query_selector_all('tbody tr')
                    print(f"   Filas en tabla: {len(rows)}")

                    for idx, row in enumerate(rows[:50]):  # Limitar a primeras 50
                        try:
                            cells = await row.query_selector_all('td')
                            if len(cells) >= 5:
                                cell_texts = []
                                for cell in cells[:6]:
                                    text = await cell.text_content()
                                    cell_texts.append(text.strip() if text else "")

                                # Filtrar por Honduras y palabras clave
                                full_text = " ".join(cell_texts).lower()
                                
                                if "honduras" in full_text and any(kw in full_text for kw in 
                                    ['construcción', 'construction', 'materials', 'materiales', 
                                     'supply', 'suministro', 'building', 'edificio', 'remodeling', 'remodelación']):
                                    
                                    proceso = {
                                        "referencia": cell_texts[0] if len(cell_texts) > 0 else "",
                                        "titulo": cell_texts[1] if len(cell_texts) > 1 else "",
                                        "pais": cell_texts[2] if len(cell_texts) > 2 else "",
                                        "tipo": cell_texts[3] if len(cell_texts) > 3 else "",
                                        "fecha_publicado": cell_texts[4] if len(cell_texts) > 4 else "",
                                        "fecha_cierre": cell_texts[5] if len(cell_texts) > 5 else ""
                                    }
                                    
                                    self.procesos.append(proceso)
                                    print(f"✅ [{len(self.procesos)}] {proceso['referencia'][:40]}...")

                        except Exception as e:
                            print(f"⚠️  Error en fila {idx}: {str(e)[:50]}")
                            continue

                else:
                    print("⚠️  No se encontraron tablas en la página")

                await browser.close()
                print(f"\n✅ Extracción completada: {len(self.procesos)} procesos para Honduras encontrados")
                return True

            except Exception as e:
                print(f"❌ Error en extracción: {e}")
                print(f"   Tipo de error: {type(e).__name__}")
                return False

    def guardar_datos(self, archivo_salida):
        """Guarda procesos en JSON"""
        datos = {
            "metadata": {
                "fuente": "UNGM - United Nations Global Marketplace",
                "url": self.base_url,
                "tipo": "Procesos de Construcción y Materiales - Honduras",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d"),
                "total_procesos": len(self.procesos),
                "moneda": "USD",
                "cobertura": "Honduras - Procesos de Construcción y Materiales",
                "filtros_aplicados": "País: Honduras, Tipos: Construcción/Materiales"
            },
            "procesos": self.procesos
        }

        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"💾 Datos guardados en: {archivo_salida}")
        print(f"   Total procesos: {len(self.procesos)}")

async def main():
    """Función principal"""
    extractor = ExtractorUNGMv2()

    print("🌍 UNGM - Extractor de Procesos Honduras v2")
    print("=" * 50)
    
    if await extractor.extraer_procesos():
        if len(extractor.procesos) > 0:
            extractor.guardar_datos('data/ungm-honduras.json')
            print("\n✅ Extracción exitosa")
        else:
            print("\n⚠️  No se encontraron procesos que coincidan con los filtros")
    else:
        print("\n❌ No se pudo completar la extracción")
        print("   Verificar conexión de red")

if __name__ == '__main__':
    asyncio.run(main())
