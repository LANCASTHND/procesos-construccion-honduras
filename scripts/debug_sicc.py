#!/usr/bin/env python3
"""Debug script para analizar estructura de SICC Honduras Compras"""

import requests
from bs4 import BeautifulSoup
import json

url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"

print("🔍 Conectando a SICC...")
try:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    print("✅ Conectado\n")

    soup = BeautifulSoup(response.content, 'html.parser')
    tablas = soup.find_all('table')

    print(f"📊 Total de tablas encontradas: {len(tablas)}\n")

    # Analizar cada tabla
    for idx, tabla in enumerate(tablas[:5]):  # Primeras 5 tablas
        filas = tabla.find_all('tr')
        print(f"TABLA {idx}: {len(filas)} filas")
        print("=" * 80)

        # Mostrar primeras 3 filas
        for f_idx, fila in enumerate(filas[:3]):
            celdas = fila.find_all(['td', 'th'])
            print(f"\n  Fila {f_idx}: {len(celdas)} celdas")

            for c_idx, celda in enumerate(celdas[:6]):  # Primeras 6 celdas
                texto = celda.text.strip()[:60]  # Primeros 60 caracteres
                print(f"    [{c_idx}]: {texto}")

        print("\n" + "-" * 80 + "\n")

except Exception as e:
    print(f"❌ Error: {e}")
