#!/usr/bin/env python3
"""
Extractor UNGM v3 - Usando curl y parsing HTML
Extrae procesos de construcción y materiales de UNGM para Honduras
"""

import json
import subprocess
import re
from datetime import datetime
from bs4 import BeautifulSoup

class ExtractorUNGMv3:
    """Extrae procesos de UNGM parseando HTML directo"""

    def __init__(self):
        self.base_url = "https://www.ungm.org/Public/Notice"
        self.procesos = []

    def descargar_html(self):
        """Descarga HTML de UNGM usando curl"""
        print("⏳ Descargando página UNGM...")
        try:
            result = subprocess.run(
                ['curl', '-s', '-L', self.base_url],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print("✅ Página descargada")
                return result.stdout
            else:
                print(f"❌ Error curl: {result.stderr}")
                return None
        except Exception as e:
            print(f"❌ Error al descargar: {e}")
            return None

    def extraer_procesos(self, html):
        """Extrae procesos del HTML"""
        print("🔍 Parseando HTML...")
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Buscar tabla de procesos
            tables = soup.find_all('table')
            print(f"   Tablas encontradas: {len(tables)}")
            
            if len(tables) == 0:
                print("⚠️  No se encontraron tablas")
                return False
            
            # Asumir que la primera tabla contiene los procesos
            table = tables[0]
            rows = table.find_all('tr')[1:]  # Saltar header
            
            print(f"   Filas encontradas: {len(rows)}")
            
            for idx, row in enumerate(rows):
                try:
                    cells = row.find_all('td')
                    if len(cells) >= 6:
                        # Extraer texto de celdas
                        referencia = cells[0].text.strip()
                        titulo = cells[1].text.strip()
                        pais = cells[2].text.strip()
                        tipo = cells[3].text.strip()
                        fecha_pub = cells[4].text.strip() if len(cells) > 4 else ""
                        fecha_cierre = cells[5].text.strip() if len(cells) > 5 else ""
                        
                        # Link
                        link = ""
                        link_elem = row.find('a')
                        if link_elem and link_elem.get('href'):
                            link = link_elem['href']
                            if not link.startswith('http'):
                                link = "https://www.ungm.org" + link
                        
                        # Filtrar por Honduras y palabras clave
                        full_text = f"{referencia} {titulo} {pais} {tipo}".lower()
                        
                        if "honduras" in full_text and any(kw in full_text for kw in 
                            ['construcción', 'construction', 'materials', 'materiales', 
                             'supply', 'suministro', 'building', 'edificio', 'remodeling', 
                             'remodelación', 'obra', 'infrastructure', 'infraestructura']):
                            
                            proceso = {
                                "referencia": referencia,
                                "titulo": titulo,
                                "pais": pais,
                                "tipo": tipo,
                                "fecha_publicado": fecha_pub,
                                "fecha_cierre": fecha_cierre,
                                "url": link
                            }
                            
                            self.procesos.append(proceso)
                            print(f"✅ [{len(self.procesos)}] {referencia[:40]}")
                
                except Exception as e:
                    print(f"⚠️  Error en fila {idx}: {str(e)[:50]}")
                    continue
            
            return True

        except Exception as e:
            print(f"❌ Error parseando: {e}")
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
    extractor = ExtractorUNGMv3()

    print("🌍 UNGM - Extractor de Procesos Honduras v3")
    print("=" * 50)
    
    html = extractor.descargar_html()
    if html:
        if extractor.extraer_procesos(html):
            if len(extractor.procesos) > 0:
                extractor.guardar_datos('data/ungm-honduras.json')
                print("\n✅ Extracción exitosa")
            else:
                print("\n⚠️  No se encontraron procesos que coincidan con los filtros")
                print("   Guardando estructura vacía para referencia...")
                extractor.guardar_datos('data/ungm-honduras.json')
        else:
            print("\n❌ Error al parsear HTML")
    else:
        print("\n❌ No se pudo descargar la página")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
