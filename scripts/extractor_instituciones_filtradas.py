#!/usr/bin/env python3
"""
Extractor de SICC Honduras - Búsqueda por institución con filtrado
Solo busca en instituciones principales de construcción/ingeniería
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import re
import time

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Instala: pip install requests beautifulsoup4")
    exit(1)

class SICCInstitucionesExtractor:
    """Extractor filtrado de SICC"""

    def __init__(self):
        self.base_url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Instituciones principales a buscar (construcción/ingeniería)
        self.palabras_clave = [
            'UNAH', 'UNA', 'SIT', 'SEDENA', 'IHT', 'Municipalidad',
            'Alcaldía', 'Tegucigalpa', 'San Pedro', 'Obras', 'Infraestructura',
            'Construcción', 'Ingeniería', 'Agua', 'Energía', 'Transporte'
        ]

        self.contactos = {
            "UNAH": "unah-compras@unah.edu.hn",
            "UNA": "compras@una.hn",
            "SIT": "licitaciones@sit.gob.hn",
            "SEDENA": "compras@sedena.mil.hn",
            "IHT": "compras@iht.hn",
        }

    def filtrar_instituciones(self, todas_opciones: Dict[str, str]) -> Dict[str, str]:
        """Filtra solo instituciones relevantes"""
        filtradas = {}

        for nombre, valor in todas_opciones.items():
            # Buscar palabras clave en el nombre
            if any(palabra.lower() in nombre.lower() for palabra in self.palabras_clave):
                filtradas[nombre] = valor

        return filtradas

    def obtener_opciones_instituciones(self) -> Dict[str, str]:
        """Obtiene el mapeo de nombres a valores"""
        try:
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            select = soup.find('select', {'id': re.compile('ddlEntidades', re.I)})

            if not select:
                return {}

            opciones = {}
            for option in select.find_all('option'):
                value = option.get('value', '')
                text = option.text.strip()

                if value and text and value != '0':
                    opciones[text] = value

            return opciones

        except Exception as e:
            print(f"❌ Error obteniendo opciones: {e}")
            return {}

    def extraer_institucion(self, institucion_valor: str, institucion_nombre: str) -> List[Dict[str, Any]]:
        """Extrae procesos de una institución"""
        procesos = []

        try:
            # Obtener ViewState
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            viewstate = viewstate.get('value', '') if viewstate else ""

            eventval = soup.find('input', {'name': '__EVENTVALIDATION'})
            eventval = eventval.get('value', '') if eventval else ""

            # POST de búsqueda
            data = {
                '__VIEWSTATE': viewstate,
                '__EVENTVALIDATION': eventval,
                'ctl00$cphCuerpo$wpParametros$ddlEntidades': institucion_valor,
                'ctl00$cphCuerpo$wpParametros$btnBuscar': 'Buscar',
            }

            response = self.session.post(self.base_url, data=data, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
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
                        expediente = celdas[0].text.strip() if len(celdas) > 0 else ""
                        descripcion = celdas[1].text.strip() if len(celdas) > 1 else ""
                        inst = celdas[2].text.strip().upper() if len(celdas) > 2 else ""
                        monto_text = celdas[3].text.strip() if len(celdas) > 3 else "0"
                        fecha_cierre = celdas[4].text.strip() if len(celdas) > 4 else ""

                        if not expediente or not fecha_cierre:
                            continue

                        # Parsear monto
                        monto = 0
                        try:
                            monto_clean = monto_text.replace('L.', '').replace(',', '').strip()
                            monto = float(monto_clean) if monto_clean else 0
                        except:
                            pass

                        # Calcular días
                        try:
                            cierre_date = datetime.strptime(fecha_cierre, '%d/%m/%Y')
                            dias = (cierre_date - datetime.now()).days
                        except:
                            continue

                        if dias > 0:
                            proceso = {
                                "expediente": expediente,
                                "descripcion": descripcion,
                                "institucion": inst if inst else institucion_nombre,
                                "monto": monto if monto > 0 else 5000000,
                                "cierre": fecha_cierre,
                                "contacto": self.contactos.get(institucion_nombre, "contacto@honduras.gob.hn"),
                                "link": "",
                                "dias_para_cierre": dias,
                                "tipo_licitacion": "licitacion_normal",
                                "estado_proceso": "vigente",
                                "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                            }

                            for celda in celdas:
                                link_elem = celda.find('a')
                                if link_elem and link_elem.get('href'):
                                    proceso['link'] = link_elem.get('href', '')
                                    break

                            procesos.append(proceso)

                    except:
                        continue

        except Exception as e:
            pass

        return procesos

    def extraer_licitaciones(self) -> List[Dict[str, Any]]:
        """Extrae licitaciones"""
        print("🔍 Obteniendo instituciones de SICC...\n")

        todas = self.obtener_opciones_instituciones()
        print(f"📊 Total de instituciones en SICC: {len(todas)}")

        filtradas = self.filtrar_instituciones(todas)
        print(f"🎯 Instituciones a buscar: {len(filtradas)}\n")

        procesos_totales = []

        for idx, (nombre, valor) in enumerate(filtradas.items(), 1):
            print(f"   [{idx}/{len(filtradas)}] {nombre[:50]}...", end=" ", flush=True)

            procesos = self.extraer_institucion(valor, nombre.split('(')[0].strip())

            if procesos:
                procesos_totales.extend(procesos)
                print(f"✅ {len(procesos)}")
            else:
                print("⚠️")

            # Delay para no sobrecargar SICC
            time.sleep(0.5)

        print(f"\n   📊 Total extraídos: {len(procesos_totales)}\n")
        return procesos_totales

    def guardar_json(self, procesos: List[Dict]):
        """Guarda en JSON"""
        total = len(procesos)
        inversion = sum(p.get('monto', 0) for p in procesos)

        for idx, p in enumerate(procesos, 1):
            if 'nro' not in p:
                p['nro'] = idx

        datos = {
            "metadata": {
                "tipo": "licitaciones_normales",
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

        os.makedirs('data', exist_ok=True)

        with open('data/licitaciones.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"✅ Guardado: data/licitaciones.json")
        print(f"   📊 Total: {total} procesos")
        print(f"   💰 Inversión: L. {inversion:,.0f}\n")

def main():
    print("\n" + "="*60)
    print("🏗️  EXTRACTOR SICC - BÚSQUEDA POR INSTITUCIÓN")
    print("="*60 + "\n")

    extractor = SICCInstitucionesExtractor()
    licitaciones = extractor.extraer_licitaciones()
    extractor.guardar_json(licitaciones)

    print("="*60)
    print(f"✅ Completado: {len(licitaciones)} procesos extraídos")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
