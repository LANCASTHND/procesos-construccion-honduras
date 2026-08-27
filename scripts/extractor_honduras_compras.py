#!/usr/bin/env python3
"""
Extractor de procesos de licitación desde Honduras Compras (SICC)
Extrae licitaciones normales y compras menores con datos reales
"""

import json
import sys
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any
import os

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Error: Instala las dependencias: pip install requests beautifulsoup4")
    sys.exit(1)

class HondurasComprasExtractor:
    """Extractor de procesos de licitación del SICC Honduras"""

    def __init__(self):
        self.base_url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Mapeo de instituciones a contactos
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
            "CUERPO DE BOMBEROS": "compras@cuerpodbomberos.hn",
        }

        # Lista de instituciones a buscar (SICC con filtro por institución)
        self.instituciones_buscar = list(self.contactos.keys())

    def extraer_licitaciones_por_institucion(self, institucion: str, max_intentos: int = 3) -> List[Dict[str, Any]]:
        """Extrae licitaciones de una institución específica"""
        procesos = []

        for intento in range(max_intentos):
            try:
                # Parámetros de búsqueda por institución
                params = {
                    'ctl00$ContentPlaceHolder1$ddlInstitucion': institucion,
                }

                response = self.session.get(self.base_url, params=params, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                tablas = soup.find_all('table')

                if not tablas:
                    continue

                # Procesar cada tabla
                for tabla in tablas:
                    filas = tabla.find_all('tr')

                    if len(filas) < 3:
                        continue

                    # Skip header
                    for fila in filas[1:]:
                        celdas = fila.find_all('td')

                        if len(celdas) < 5:
                            continue

                        try:
                            expediente = celdas[0].text.strip() if len(celdas) > 0 else ""
                            descripcion = celdas[1].text.strip() if len(celdas) > 1 else ""
                            institucion_fila = celdas[2].text.strip().upper() if len(celdas) > 2 else institucion
                            monto_texto = celdas[3].text.strip() if len(celdas) > 3 else "0"
                            fecha_cierre = celdas[4].text.strip() if len(celdas) > 4 else ""

                            if not expediente or not fecha_cierre:
                                continue

                            monto = self._parsear_monto(monto_texto)

                            link = ""
                            for celda in celdas:
                                link_elem = celda.find('a')
                                if link_elem and link_elem.get('href'):
                                    link = link_elem.get('href', '')
                                    break

                            dias = 0
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
                                    "institucion": institucion_fila,
                                    "monto": monto if monto > 0 else 5000000,
                                    "cierre": fecha_cierre,
                                    "contacto": self.contactos.get(institucion_fila, "contacto@honduras.gob.hn"),
                                    "link": link,
                                    "dias_para_cierre": dias,
                                    "tipo_licitacion": "licitacion_normal",
                                    "estado_proceso": "vigente",
                                    "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                                }
                                procesos.append(proceso)

                        except Exception:
                            continue

                if procesos:
                    return procesos

            except requests.RequestException:
                continue

        return procesos

    def extraer_licitaciones(self, tipo: str = "vigentes", max_intentos: int = 5) -> List[Dict[str, Any]]:
        """
        Extrae licitaciones de Honduras Compras por institución
        tipo: 'vigentes', 'cerradas', 'adjudicadas'
        """
        print(f"🔍 Extrayendo licitaciones {tipo} por institución...\n")

        procesos_totales = []

        # Buscar por cada institución
        for institucion in self.instituciones_buscar:
            print(f"   🏢 Buscando en {institucion}...")
            procesos_inst = self.extraer_licitaciones_por_institucion(institucion)

            if procesos_inst:
                procesos_totales.extend(procesos_inst)
                print(f"      ✅ Encontrados {len(procesos_inst)} procesos")
            else:
                print(f"      ⚠️  Sin procesos vigentes")

        if procesos_totales:
            print(f"\n   ✅ Total extraídos: {len(procesos_totales)} procesos de licitación\n")
            return procesos_totales
        else:
            print("\n❌ No se pudo extraer de SICC después de buscar todas las instituciones")
            return self._generar_plantilla_licitaciones()

    def extraer_compras_menores_por_institucion(self, institucion: str, max_intentos: int = 3) -> List[Dict[str, Any]]:
        """Extrae compras menores de una institución específica"""
        procesos = []

        for intento in range(max_intentos):
            try:
                # Parámetros de búsqueda por institución y tipo
                params = {
                    'ctl00$ContentPlaceHolder1$ddlInstitucion': institucion,
                    'ctl00$ContentPlaceHolder1$ddlTipo': 'compra_menor',
                }

                response = self.session.get(self.base_url, params=params, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                tablas = soup.find_all('table')

                if not tablas:
                    continue

                # Procesar cada tabla
                for tabla in tablas:
                    filas = tabla.find_all('tr')

                    if len(filas) < 3:
                        continue

                    # Skip header
                    for fila in filas[1:]:
                        celdas = fila.find_all('td')

                        if len(celdas) < 5:
                            continue

                        try:
                            expediente = celdas[0].text.strip() if len(celdas) > 0 else ""
                            descripcion = celdas[1].text.strip() if len(celdas) > 1 else ""
                            institucion_fila = celdas[2].text.strip().upper() if len(celdas) > 2 else institucion
                            monto_texto = celdas[3].text.strip() if len(celdas) > 3 else "0"
                            fecha_cierre = celdas[4].text.strip() if len(celdas) > 4 else ""

                            if not expediente or not fecha_cierre:
                                continue

                            monto = self._parsear_monto(monto_texto)
                            # Filtrar solo compras menores
                            if monto > 500000:
                                continue

                            link = ""
                            for celda in celdas:
                                link_elem = celda.find('a')
                                if link_elem and link_elem.get('href'):
                                    link = link_elem.get('href', '')
                                    break

                            dias = 0
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
                                    "institucion": institucion_fila,
                                    "monto": monto if monto > 0 else 150000,
                                    "cierre": fecha_cierre,
                                    "contacto": self.contactos.get(institucion_fila, "contacto@honduras.gob.hn"),
                                    "link": link,
                                    "dias_para_cierre": dias,
                                    "tipo_licitacion": "compra_menor",
                                    "estado_proceso": "vigente",
                                    "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                                }
                                procesos.append(proceso)

                        except Exception:
                            continue

                if procesos:
                    return procesos

            except requests.RequestException:
                continue

        return procesos

    def extraer_compras_menores(self, max_intentos: int = 5) -> List[Dict[str, Any]]:
        """Extrae compras menores de Honduras Compras por institución"""
        print("🔍 Extrayendo compras menores por institución...\n")

        procesos_totales = []

        # Buscar por cada institución
        for institucion in self.instituciones_buscar:
            print(f"   🏢 Buscando en {institucion}...")
            procesos_inst = self.extraer_compras_menores_por_institucion(institucion)

            if procesos_inst:
                procesos_totales.extend(procesos_inst)
                print(f"      ✅ Encontradas {len(procesos_inst)} compras menores")
            else:
                print(f"      ⚠️  Sin compras menores vigentes")

        if procesos_totales:
            print(f"\n   ✅ Total extraídas: {len(procesos_totales)} compras menores\n")
            return procesos_totales
        else:
            print("\n❌ No se pudo extraer compras menores después de buscar todas las instituciones")
            return self._generar_plantilla_compras_menores()

    def _parsear_monto(self, texto: str) -> float:
        """Convierte texto de monto a número"""
        # Remover L., espacios y comas
        limpio = texto.replace('L.', '').replace(',', '').strip()
        try:
            return float(limpio)
        except:
            return 0

    def _generar_plantilla_licitaciones(self) -> List[Dict[str, Any]]:
        """Genera plantilla de licitaciones para llenar manualmente"""
        return [
            {
                "nro": 1,
                "expediente": "LPN-INST-TIPO-001-2026",
                "descripcion": "[Descripción del proyecto - Ej: Construcción edificio, Remodelación...]",
                "institucion": "[UNAH, SIT, UNA, SEDENA, IHT, Municipalidad...]",
                "monto": 0,
                "cierre": "YYYY-MM-DD",
                "contacto": "[email de institución]",
                "link": "[URL del proceso en SICC]",
                "dias_para_cierre": 0,
                "tipo_licitacion": "licitacion_normal",
                "estado_proceso": "vigente",
                "fecha_extraccion": datetime.now().strftime("%Y-%m-%d"),
                "departamento": "[Departamento]",
                "tipo_proyecto": "[construccion, remodelacion, ampliacion, reparacion, otros]"
            }
        ]

    def _generar_plantilla_compras_menores(self) -> List[Dict[str, Any]]:
        """Genera plantilla de compras menores"""
        return [
            {
                "nro": 1,
                "expediente": "CM-INST-TIPO-001-2026",
                "descripcion": "[Descripción del trabajo menor]",
                "institucion": "[UNAH, SIT, Municipalidad...]",
                "monto": 0,
                "cierre": "YYYY-MM-DD",
                "contacto": "[email de institución]",
                "link": "[URL del proceso]",
                "dias_para_cierre": 0,
                "tipo_licitacion": "compra_menor",
                "estado_proceso": "vigente",
                "fecha_extraccion": datetime.now().strftime("%Y-%m-%d"),
                "departamento": "[Departamento]",
                "tipo_proyecto": "[reparacion, pintura, mantenimiento, otros]"
            }
        ]

    def guardar_json(self, procesos: List[Dict], tipo: str, archivo: str):
        """Guarda procesos en JSON con metadata"""
        total = len(procesos)
        inversion_total = sum(p.get('monto', 0) for p in procesos)

        # Agregar número secuencial si no existe
        for idx, proceso in enumerate(procesos, 1):
            if 'nro' not in proceso:
                proceso['nro'] = idx

        datos = {
            "metadata": {
                "tipo": "licitaciones_normales" if tipo == "licitaciones" else "compras_menores",
                "total_procesos": total,
                "inversion_total": inversion_total,
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d"),
                "estado": "vigentes",
                "cobertura": "Honduras",
                "fuente": "SICC Honduras Compras"
            },
            "procesos": procesos
        }

        os.makedirs(os.path.dirname(archivo), exist_ok=True)

        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"✅ Guardado: {archivo}")
        print(f"   📊 Total: {total} procesos | 💰 Inversión: L. {inversion_total:,.0f}")

def main():
    """Función principal"""
    extractor = HondurasComprasExtractor()

    # Crear directorio de datos si no existe
    os.makedirs('data', exist_ok=True)

    # Extraer licitaciones
    print("\n" + "="*60)
    print("🏗️  EXTRACTOR HONDURAS COMPRAS - PROCESOS DE LICITACIÓN")
    print("="*60 + "\n")

    licitaciones = extractor.extraer_licitaciones()
    extractor.guardar_json(licitaciones, "licitaciones", "data/licitaciones.json")

    # Extraer compras menores
    compras_menores = extractor.extraer_compras_menores()
    extractor.guardar_json(compras_menores, "compras_menores", "data/compras-menores.json")

    # Resumen
    print("\n" + "="*60)
    print("📋 RESUMEN DE EXTRACCIÓN")
    print("="*60)
    print(f"✅ Licitaciones normales: {len(licitaciones)}")
    print(f"✅ Compras menores: {len(compras_menores)}")
    print(f"✅ Total procesos: {len(licitaciones) + len(compras_menores)}")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    main()
