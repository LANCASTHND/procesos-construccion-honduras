#!/usr/bin/env python3
"""Extractor mejorado para SICC Honduras Compras con búsqueda de patrones"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import os

class ExtractorMejorado:
    def __init__(self):
        self.base_url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def extraer_procesos(self):
        """Extrae procesos buscando patrones de expedientes"""
        print("🔍 Extrayendo procesos con búsqueda de patrones...")

        try:
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()

            html_text = response.text

            # Buscar patrones de expedientes (ej: LPN-UNAH-0001-2026)
            # Patrón: Letras-Letras-números-Año
            patron_expediente = r'([A-Z]{2,4}-[A-Z\s]{3,15}-\d{2,4}-202[0-9])'
            expedientes = re.findall(patron_expediente, html_text)

            print(f"✅ Expedientes encontrados: {len(set(expedientes))}")
            print(f"   {set(expedientes)}\n")

            # Buscar fechas (DD/MM/YYYY)
            patron_fecha = r'(\d{2}/\d{2}/202[0-9])'
            fechas = re.findall(patron_fecha, html_text)
            print(f"✅ Fechas encontradas: {len(set(fechas))}")
            print(f"   {list(set(fechas))[:10]}\n")

            # Buscar montos (L. XXXXX)
            patron_monto = r'L\.\s+([\d,\.]+)'
            montos = re.findall(patron_monto, html_text)
            print(f"✅ Montos encontrados: {len(set(montos))}")
            print(f"   {list(set(montos))[:10]}\n")

            # Buscar instituciones conocidas
            instituciones = ['UNAH', 'UNA', 'UNACIFOR', 'SIT', 'SEDENA', 'SESEGU', 'IHT']
            for inst in instituciones:
                if inst in html_text:
                    count = html_text.count(inst)
                    print(f"   ✓ {inst}: {count} menciones")

            # Buscar en div o span con clase que indique resultado
            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar divs o spans con texto que parezca descripción de proyecto
            palabras_clave = ['Construcción', 'Remodelación', 'Reparación', 'Ampliación', 'Equipamiento']
            coincidencias = {}

            for palabra in palabras_clave:
                elementos = soup.find_all(string=re.compile(palabra, re.I))
                if elementos:
                    coincidencias[palabra] = len(elementos)
                    print(f"   ✓ {palabra}: {len(elementos)} coincidencias")

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    extractor = ExtractorMejorado()
    extractor.extraer_procesos()
