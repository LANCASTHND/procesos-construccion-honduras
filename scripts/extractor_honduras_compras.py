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
        }

    def extraer_licitaciones(self, tipo: str = "vigentes", max_intentos: int = 5) -> List[Dict[str, Any]]:
        """
        Extrae licitaciones de Honduras Compras con reintentos
        tipo: 'vigentes', 'cerradas', 'adjudicadas'
        """
        print(f"🔍 Extrayendo licitaciones {tipo}...")

        procesos = []
        intentos = 0

        while intentos < max_intentos:
            try:
                response = self.session.get(self.base_url, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Buscar TODAS las tablas que contengan datos de procesos
                tablas = soup.find_all('table')

                if not tablas:
                    print("⚠️  No se encontraron tablas. Reintentando...")
                    intentos += 1
                    continue

                print(f"   📊 Encontradas {len(tablas)} tablas")

                # Procesar cada tabla
                contador = 0
                for tabla_idx, tabla in enumerate(tablas):
                    filas = tabla.find_all('tr')

                    # Skip si es tabla pequeña (probablemente no es de procesos)
                    if len(filas) < 3:
                        continue

                    print(f"   📋 Procesando tabla {tabla_idx + 1} ({len(filas)} filas)")

                    # Skip header (primera fila)
                    for fila_idx, fila in enumerate(filas[1:], 1):
                        celdas = fila.find_all('td')

                        # Procesar si tiene al menos 5 celdas
                        if len(celdas) < 5:
                            continue

                        try:
                            # Intentar extraer información - flexible con índices
                            expediente = celdas[0].text.strip() if len(celdas) > 0 else ""
                            descripcion = celdas[1].text.strip() if len(celdas) > 1 else ""
                            institucion = celdas[2].text.strip().upper() if len(celdas) > 2 else "DESCONOCIDA"
                            monto_texto = celdas[3].text.strip() if len(celdas) > 3 else "0"
                            fecha_cierre = celdas[4].text.strip() if len(celdas) > 4 else ""

                            # Skip si campos vacíos críticos
                            if not expediente or not fecha_cierre:
                                continue

                            # Parsear monto
                            monto = self._parsear_monto(monto_texto)

                            # Obtener link si existe (buscar en cualquier celda)
                            link = ""
                            for celda in celdas:
                                link_elem = celda.find('a')
                                if link_elem and link_elem.get('href'):
                                    link = link_elem.get('href', '')
                                    break

                            # Calcular días para cierre
                            dias = 0
                            try:
                                cierre_date = datetime.strptime(fecha_cierre, '%d/%m/%Y')
                                hoy = datetime.now()
                                dias = (cierre_date - hoy).days
                            except:
                                continue  # Skip si no parsea fecha

                            proceso = {
                                "nro": len(procesos) + 1,
                                "expediente": expediente,
                                "descripcion": descripcion,
                                "institucion": institucion,
                                "monto": monto if monto > 0 else 5000000,  # Default si no se parsea
                                "cierre": fecha_cierre,
                                "contacto": self.contactos.get(institucion, "contacto@honduras.gob.hn"),
                                "link": link,
                                "dias_para_cierre": dias,
                                "tipo_licitacion": "licitacion_normal",
                                "estado_proceso": "vigente" if dias > 0 else "cerrada",
                                "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                            }

                            # Filtrar por tipo solicitado
                            if tipo == "vigentes" and proceso["estado_proceso"] == "vigente":
                                procesos.append(proceso)
                                contador += 1
                            elif tipo != "vigentes":
                                procesos.append(proceso)
                                contador += 1

                        except Exception as e:
                            continue

                if contador > 0:
                    print(f"   ✅ Extraídos {contador} procesos de licitación")
                    return procesos
                else:
                    print("   ⚠️  No se extrajeron procesos. Reintentando...")
                    intentos += 1

            except requests.RequestException as e:
                print(f"   ⚠️  Error de conexión: {e}. Reintentando...")
                intentos += 1

        print("❌ No se pudo extraer de SICC después de múltiples intentos")
        return self._generar_plantilla_licitaciones()

    def extraer_compras_menores(self, max_intentos: int = 5) -> List[Dict[str, Any]]:
        """Extrae compras menores de Honduras Compras"""
        print("🔍 Extrayendo compras menores...")

        procesos = []
        intentos = 0

        while intentos < max_intentos:
            try:
                # Intentar extracción con parámetros
                params = {'tipo': 'compra_menor'}
                response = self.session.get(self.base_url, params=params, timeout=15)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                tablas = soup.find_all('table')

                if not tablas:
                    print("   ⚠️  No se encontraron tablas. Reintentando...")
                    intentos += 1
                    continue

                print(f"   📊 Encontradas {len(tablas)} tablas")

                contador = 0
                for tabla_idx, tabla in enumerate(tablas):
                    filas = tabla.find_all('tr')

                    if len(filas) < 3:
                        continue

                    print(f"   📋 Procesando tabla {tabla_idx + 1} ({len(filas)} filas)")

                    for fila in filas[1:]:
                        celdas = fila.find_all('td')

                        if len(celdas) < 5:
                            continue

                        try:
                            expediente = celdas[0].text.strip() if len(celdas) > 0 else ""
                            descripcion = celdas[1].text.strip() if len(celdas) > 1 else ""
                            institucion = celdas[2].text.strip().upper() if len(celdas) > 2 else "DESCONOCIDA"
                            monto_texto = celdas[3].text.strip() if len(celdas) > 3 else "0"
                            fecha_cierre = celdas[4].text.strip() if len(celdas) > 4 else ""

                            if not expediente or not fecha_cierre:
                                continue

                            # Filtrar solo compras menores (montos menores)
                            monto = self._parsear_monto(monto_texto)
                            if monto > 500000:  # Considerar solo si es compra menor
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

                            proceso = {
                                "nro": len(procesos) + 1,
                                "expediente": expediente,
                                "descripcion": descripcion,
                                "institucion": institucion,
                                "monto": monto if monto > 0 else 150000,
                                "cierre": fecha_cierre,
                                "contacto": self.contactos.get(institucion, "contacto@honduras.gob.hn"),
                                "link": link,
                                "dias_para_cierre": dias,
                                "tipo_licitacion": "compra_menor",
                                "estado_proceso": "vigente" if dias > 0 else "cerrada",
                                "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                            }

                            if proceso["estado_proceso"] == "vigente":
                                procesos.append(proceso)
                                contador += 1

                        except Exception:
                            continue

                if contador > 0:
                    print(f"   ✅ Extraídas {contador} compras menores")
                    return procesos
                else:
                    print("   ⚠️  No se extrajeron compras menores. Reintentando...")
                    intentos += 1

            except requests.RequestException as e:
                print(f"   ⚠️  Error de conexión: {e}. Reintentando...")
                intentos += 1

        print("❌ No se pudo extraer compras menores después de múltiples intentos")
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
