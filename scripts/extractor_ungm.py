#!/usr/bin/env python3
"""
Extractor de procesos de construcción desde UNGM (United Nations Global Marketplace)
Busca procesos de Honduras relacionados con construcción, ingeniería y materiales
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

class ExtractorUNGM:
    """Extrae procesos de construcción de UNGM Honduras"""

    def __init__(self):
        self.base_url = "https://www.ungm.org/Public/Notice"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def extraer_procesos(self) -> tuple:
        """Extrae procesos de UNGM Honduras"""

        print("🔍 Extrayendo procesos de UNGM Honduras...\n")

        procesos = []

        try:
            # Buscar procesos de Honduras con filtros
            url = f"{self.base_url}?f=1&ctrCode=HN"

            print(f"📍 Accediendo a UNGM: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar tabla de resultados
            resultados = soup.find_all('div', class_='row')

            if not resultados:
                print("⚠️  No se encontraron procesos en UNGM")
                return [], []

            print(f"📊 Encontrados {len(resultados)} registros")

            for item in resultados[:20]:  # Primeros 20
                try:
                    # Extraer información
                    titulo = item.find('a', class_='blue-link')
                    if not titulo:
                        continue

                    desc = titulo.text.strip()

                    # Filtrar por palabras clave de construcción
                    palabras_construccion = [
                        'construcción', 'construccion', 'engineering', 'ingeniería',
                        'building', 'infrastructure', 'civil', 'obra', 'materiales'
                    ]

                    if not any(palabra.lower() in desc.lower() for palabra in palabras_construccion):
                        continue

                    # Extraer fecha
                    fecha_elem = item.find('span', class_='date')
                    fecha = fecha_elem.text.strip() if fecha_elem else ""

                    proceso = {
                        "fuente": "UNGM",
                        "titulo": desc[:150],
                        "descripcion": desc,
                        "pais": "Honduras",
                        "fecha_publicacion": fecha,
                        "link": titulo.get('href', ''),
                        "tipo": "internacional",
                        "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                    }

                    procesos.append(proceso)
                    print(f"   ✓ {desc[:60]}...")

                except Exception as e:
                    continue

            print(f"\n✅ Extraídos {len(procesos)} procesos de construcción de UNGM")

        except requests.ConnectionError:
            print("❌ Error de conexión a UNGM")
        except requests.Timeout:
            print("⏱️  Timeout conectando a UNGM")
        except Exception as e:
            print(f"❌ Error: {e}")

        return procesos, []

    def guardar_resultados(self, procesos: List[Dict]):
        """Guarda resultados en JSON"""

        datos = {
            "metadata": {
                "tipo": "procesos_ungm_honduras",
                "total_procesos": len(procesos),
                "pais": "Honduras",
                "fuente": "UNGM - United Nations Global Marketplace",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d"),
                "hora_actualizacion": datetime.now().strftime("%H:%M:%S"),
                "filtros": "Procesos de construcción e ingeniería"
            },
            "procesos": procesos
        }

        os.makedirs('data', exist_ok=True)
        with open('data/ungm_honduras.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"✅ data/ungm_honduras.json - {len(procesos)} procesos")

def main():
    print("\n" + "="*70)
    print("🌐 EXTRACTOR UNGM - HONDURAS")
    print("="*70 + "\n")

    extractor = ExtractorUNGM()
    procesos, _ = extractor.extraer_procesos()
    extractor.guardar_resultados(procesos)

    print("\n" + "="*70)
    print("✅ EXTRACCIÓN COMPLETADA")
    print(f"📊 Procesos de UNGM: {len(procesos)}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
