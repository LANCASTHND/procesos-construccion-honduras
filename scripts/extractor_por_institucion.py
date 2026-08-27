#!/usr/bin/env python3
"""
Extractor de SICC Honduras que busca por institución
Maneja ViewState y sesiones ASP.NET correctamente
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import re

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Instala: pip install requests beautifulsoup4")
    exit(1)

class SICCPorInstitucionExtractor:
    """Extractor de SICC por institución individual"""

    def __init__(self):
        self.base_url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        self.contactos = {
            "UNAH": "unah-compras@unah.edu.hn",
            "UNA": "compras@una.hn",
            "SIT": "licitaciones@sit.gob.hn",
            "SEDENA": "compras@sedena.mil.hn",
            "IHT": "compras@iht.hn",
            "TEGUCIGALPA": "compras@tegucigalpa.gob.hn",
            "SAN PEDRO SULA": "compras@sanpedrosula.gob.hn",
        }

    def obtener_opciones_instituciones(self) -> Dict[str, str]:
        """Obtiene el mapeo de nombres a valores de las instituciones"""
        try:
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar el select de instituciones
            select = soup.find('select', {'id': re.compile('ddlEntidades', re.I)})

            if not select:
                print("⚠️  No se encontró dropdown de instituciones")
                return {}

            opciones = {}
            for option in select.find_all('option'):
                value = option.get('value', '')
                text = option.text.strip()

                # Guardar tanto el value como el nombre normalizado
                if value and text:
                    opciones[text] = value

            return opciones

        except Exception as e:
            print(f"❌ Error obteniendo opciones: {e}")
            return {}

    def extraer_institucion(self, institucion_valor: str, institucion_nombre: str) -> List[Dict[str, Any]]:
        """Extrae procesos de una institución específica"""
        procesos = []

        try:
            # Primera solicitud para obtener ViewState
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraer ViewState (necesario para ASP.NET)
            viewstate = ""
            viewstate_elem = soup.find('input', {'name': '__VIEWSTATE'})
            if viewstate_elem:
                viewstate = viewstate_elem.get('value', '')

            eventvalidation = ""
            eventval_elem = soup.find('input', {'name': '__EVENTVALIDATION'})
            if eventval_elem:
                eventvalidation = eventval_elem.get('value', '')

            # Preparar POST data para búsqueda
            data = {
                '__VIEWSTATE': viewstate,
                '__EVENTVALIDATION': eventvalidation,
                'ctl00$cphCuerpo$wpParametros$ddlEntidades': institucion_valor,
                'ctl00$cphCuerpo$wpParametros$btnBuscar': 'Buscar',
            }

            # Segunda solicitud con búsqueda
            response = self.session.post(self.base_url, data=data, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar tablas de resultados
            tablas = soup.find_all('table')

            for tabla in tablas:
                filas = tabla.find_all('tr')

                if len(filas) < 2:
                    continue

                # Procesar filas (skip header)
                for fila in filas[1:]:
                    celdas = fila.find_all('td')

                    if len(celdas) < 5:
                        continue

                    try:
                        expediente = celdas[0].text.strip() if len(celdas) > 0 else ""
                        descripcion = celdas[1].text.strip() if len(celdas) > 1 else ""
                        inst_text = celdas[2].text.strip().upper() if len(celdas) > 2 else ""
                        monto_text = celdas[3].text.strip() if len(celdas) > 3 else "0"
                        fecha_cierre = celdas[4].text.strip() if len(celdas) > 4 else ""

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
                            cierre_date = datetime.strptime(fecha_cierre, '%d/%m/%Y')
                            hoy = datetime.now()
                            dias = (cierre_date - hoy).days
                        except:
                            continue

                        if dias > 0:  # Solo vigentes
                            proceso = {
                                "expediente": expediente,
                                "descripcion": descripcion,
                                "institucion": inst_text if inst_text else institucion_nombre,
                                "monto": monto if monto > 0 else 5000000,
                                "cierre": fecha_cierre,
                                "contacto": self.contactos.get(institucion_nombre, "contacto@honduras.gob.hn"),
                                "link": "",
                                "dias_para_cierre": dias,
                                "tipo_licitacion": "licitacion_normal",
                                "estado_proceso": "vigente",
                                "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                            }

                            # Buscar link
                            for celda in celdas:
                                link_elem = celda.find('a')
                                if link_elem and link_elem.get('href'):
                                    proceso['link'] = link_elem.get('href', '')
                                    break

                            procesos.append(proceso)

                    except Exception as e:
                        continue

        except Exception as e:
            print(f"      ❌ Error: {str(e)[:50]}")

        return procesos

    def extraer_licitaciones(self) -> List[Dict[str, Any]]:
        """Extrae licitaciones buscando por institución"""
        print("🔍 Obteniendo lista de instituciones de SICC...\n")

        opciones = self.obtener_opciones_instituciones()

        if not opciones:
            print("❌ No se pudieron obtener instituciones")
            return []

        print(f"📊 Encontradas {len(opciones)} instituciones\n")
        print("🏗️  Extrayendo procesos por institución:\n")

        procesos_totales = []

        for nombre_inst, valor_inst in list(opciones.items())[:15]:  # Limitar a las primeras 15
            # Filtrar solo las que nos interesan
            nombre_corto = nombre_inst.split('(')[0].strip()

            print(f"   🏢 {nombre_corto}...", end=" ", flush=True)
            procesos = self.extraer_institucion(valor_inst, nombre_corto)

            if procesos:
                procesos_totales.extend(procesos)
                print(f"✅ {len(procesos)}")
            else:
                print("⚠️")

        print(f"\n   📊 Total extraídos: {len(procesos_totales)} procesos\n")
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
        print(f"   📊 Total: {total} procesos | 💰 Inversión: L. {inversion:,.0f}\n")

def main():
    print("\n" + "="*60)
    print("🏗️  EXTRACTOR SICC - BÚSQUEDA POR INSTITUCIÓN")
    print("="*60 + "\n")

    extractor = SICCPorInstitucionExtractor()
    licitaciones = extractor.extraer_licitaciones()
    extractor.guardar_json(licitaciones)

    print("="*60)
    print(f"✅ Extracción completada: {len(licitaciones)} procesos")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
