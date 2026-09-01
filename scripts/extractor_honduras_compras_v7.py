#!/usr/bin/env python3
"""
Extractor v7 - Batch Processing: Procesa 500 instituciones en lotes
Evita timeout procesando en grupos + guardando progreso
"""

import json
import sys
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
import os

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Error: pip install playwright")
    sys.exit(1)

class SICCExtractorV7:
    """Extractor v7 - Batch processing con checkpoints"""

    def __init__(self):
        self.base_url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"
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
            "PRONADERS": "compras@pronaders.hn",
            "DISTRITO CENTRAL": "compras@distritocental.hn",
        }
        self.palabras_construccion = [
            'construcción', 'obra', 'remodelación', 'ingeniería', 'supervisión',
            'pavimentación', 'infraestructura', 'mejoramiento', 'edificio', 'vial',
            'carretera', 'puente', 'drenaje', 'alcantarillado', 'agua potable',
            'servicios de ingeniería', 'diseño', 'ampliación', 'renovación'
        ]
        self.checkpoint_file = "scripts/.extractor_v7_checkpoint.json"

    def _cargar_checkpoint(self) -> Dict[str, Any]:
        """Carga progreso anterior si existe"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "licitaciones": [],
            "compras_menores": [],
            "instituciones_procesadas": [],
            "instituciones_fallidas": [],
            "ultima_institucion": "",
            "inicio": datetime.now().isoformat()
        }

    def _guardar_checkpoint(self, checkpoint: Dict[str, Any]):
        """Guarda progreso"""
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, default=str)

    def _es_proceso_construccion(self, expediente: str, modalidad: str, etapa: str) -> bool:
        """Verifica si el proceso es de construcción/ingeniería"""
        texto = f"{expediente} {modalidad} {etapa}".lower()
        return any(palabra in texto for palabra in self.palabras_construccion)

    def _obtener_todas_instituciones(self, page) -> Dict[str, str]:
        """Extrae dinámicamente TODAS las instituciones del dropdown"""
        print("🔍 Descubriendo instituciones...")
        instituciones = {}

        try:
            page.goto(self.base_url, wait_until='load', timeout=30000)
            time.sleep(1)

            select_elem = page.query_selector('#ctl00_cphCuerpo_wpParametros_ddlEntidades')
            if not select_elem:
                print("❌ No se encontró dropdown")
                return instituciones

            opciones = page.query_selector_all('#ctl00_cphCuerpo_wpParametros_ddlEntidades option')
            print(f"📋 Encontradas {len(opciones)} opciones")

            for opcion in opciones:
                try:
                    value = opcion.get_attribute('value')
                    texto = opcion.text_content().strip()

                    if not value or value == '0' or 'seleccione' in texto.lower():
                        continue

                    nombre_limpio = texto.strip()
                    if nombre_limpio and len(nombre_limpio) > 2:
                        instituciones[value] = nombre_limpio

                except Exception:
                    continue

            print(f"✅ Total: {len(instituciones)} instituciones\n")

        except Exception as e:
            print(f"❌ Error: {e}\n")

        return instituciones

    def _extraer_con_paginacion(self, page, tipo: str = "licitacion") -> List[Dict[str, Any]]:
        """Extrae procesos de TODAS las páginas"""
        procesos = []
        pagina = 1
        ahora = datetime.now()

        while pagina <= 50:  # Máximo 50 páginas por institución
            try:
                # Extraer tabla actual
                filas = page.query_selector_all('table[id*="gvResultados"] tbody tr')

                if not filas:
                    break

                for fila in filas:
                    try:
                        celdas = fila.query_selector_all('td')
                        if len(celdas) < 8:
                            continue

                        expediente = celdas[1].text_content().strip()
                        descripcion = celdas[2].text_content().strip()
                        modalidad = celdas[3].text_content().strip()
                        etapa = celdas[4].text_content().strip()
                        cierre_text = celdas[5].text_content().strip()
                        monto_text = celdas[6].text_content().strip()

                        # Filtro de construcción
                        if not self._es_proceso_construccion(expediente, modalidad, etapa):
                            continue

                        # Parsear fecha
                        try:
                            fecha_cierre = datetime.strptime(cierre_text, "%d/%m/%Y")
                            if fecha_cierre.year < 2026 or fecha_cierre < ahora:
                                continue
                        except:
                            continue

                        dias = (fecha_cierre - ahora).days

                        # Limpiar monto
                        monto = 0
                        try:
                            monto = int(''.join(filter(str.isdigit, monto_text)))
                        except:
                            pass

                        # Link
                        link_elem = celdas[0].query_selector('a')
                        link = link_elem.get_attribute('href') if link_elem else ""

                        proceso = {
                            "expediente": expediente,
                            "descripcion": descripcion,
                            "modalidad": modalidad,
                            "etapa": etapa,
                            "cierre": cierre_text,
                            "monto": monto,
                            "dias_para_cierre": dias,
                            "tipo_licitacion": tipo,
                            "link": link,
                            "estado_proceso": "vigente",
                            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                        }

                        procesos.append(proceso)

                    except Exception as e:
                        continue

                # Buscar botón siguiente
                try:
                    btn_siguiente = page.query_selector('a[id*="lnkSiguiente"]')
                    if not btn_siguiente or 'disabled' in btn_siguiente.get_attribute('class', ''):
                        break

                    btn_siguiente.click()
                    time.sleep(0.5)
                    pagina += 1

                except Exception:
                    break

            except Exception as e:
                print(f"     ⚠️  Error en página {pagina}: {e}")
                break

        return procesos

    def extraer_lotes(self, tam_lote: int = 50):
        """Procesa instituciones en lotes para evitar timeout"""
        print("=" * 60)
        print("EXTRACTOR v7 - BATCH PROCESSING")
        print("=" * 60 + "\n")

        checkpoint = self._cargar_checkpoint()
        print(f"📊 Retomando desde: {len(checkpoint['instituciones_procesadas'])} instituciones\n")

        licitaciones = checkpoint['licitaciones']
        compras_menores = checkpoint['compras_menores']

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(30000)

                # Obtener todas las instituciones
                todas_instituciones = self._obtener_todas_instituciones(page)

                # Filtrar ya procesadas
                pendientes = [
                    (k, v) for k, v in todas_instituciones.items()
                    if k not in checkpoint['instituciones_procesadas']
                ]

                print(f"📋 Total: {len(todas_instituciones)} | Procesadas: {len(checkpoint['instituciones_procesadas'])} | Pendientes: {len(pendientes)}\n")

                # Procesar en lotes
                for lote_num in range(0, len(pendientes), tam_lote):
                    lote = pendientes[lote_num:lote_num + tam_lote]
                    print(f"🔄 LOTE {lote_num // tam_lote + 1}: Instituciones {lote_num + 1}-{min(lote_num + tam_lote, len(pendientes))}\n")

                    for inst_id, inst_nombre in lote:
                        try:
                            print(f"   📍 {inst_nombre}...", end=" ", flush=True)

                            # Navegar a búsqueda
                            page.goto(self.base_url, wait_until='load', timeout=30000)
                            time.sleep(0.3)

                            # Seleccionar institución
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlEntidades', inst_id)
                            time.sleep(0.5)

                            # Procesar licitaciones
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipos', 'licitacion')
                            time.sleep(1)

                            procs_lic = self._extraer_con_paginacion(page, "licitacion")

                            for proc in procs_lic:
                                proc['institucion'] = inst_nombre
                                proc['contacto'] = self.contactos.get(
                                    inst_nombre.split()[0].upper(),
                                    "no-disponible@hnd.gob.hn"
                                )
                                licitaciones.append(proc)

                            # Procesar compras menores
                            page.goto(self.base_url, wait_until='load', timeout=30000)
                            time.sleep(0.3)
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlEntidades', inst_id)
                            time.sleep(0.5)
                            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipos', 'compra_menor')
                            time.sleep(1)

                            procs_cm = self._extraer_con_paginacion(page, "compra_menor")

                            for proc in procs_cm:
                                proc['institucion'] = inst_nombre
                                proc['contacto'] = self.contactos.get(
                                    inst_nombre.split()[0].upper(),
                                    "no-disponible@hnd.gob.hn"
                                )
                                compras_menores.append(proc)

                            print(f"✓ ({len(procs_lic)}L + {len(procs_cm)}C)")
                            checkpoint['instituciones_procesadas'].append(inst_id)

                        except Exception as e:
                            print(f"✗ Error: {str(e)[:40]}")
                            checkpoint['instituciones_fallidas'].append({
                                'institucion': inst_nombre,
                                'error': str(e)
                            })
                            continue

                        # Guardar checkpoint después de cada institución
                        checkpoint['licitaciones'] = licitaciones
                        checkpoint['compras_menores'] = compras_menores
                        self._guardar_checkpoint(checkpoint)

                    print()  # Salto de línea entre lotes

                browser.close()

        except Exception as e:
            print(f"❌ Error general: {e}")
            return False

        # Consolidar datos
        self._consolidar_datos(licitaciones, compras_menores, checkpoint)
        return True

    def _consolidar_datos(self, licitaciones: List, compras_menores: List, checkpoint: Dict):
        """Consolida datos finales en JSON"""
        print("\n" + "=" * 60)
        print("📊 CONSOLIDANDO DATOS")
        print("=" * 60 + "\n")

        # Eliminar duplicados y filtrar
        licitaciones = self._eliminar_duplicados(licitaciones)
        compras_menores = self._eliminar_duplicados(compras_menores)

        # Filtrar vigentes
        licitaciones = [p for p in licitaciones if p.get('dias_para_cierre', -1) >= 0 and p.get('estado_proceso') == 'vigente']
        compras_menores = [p for p in compras_menores if p.get('dias_para_cierre', -1) >= 0 and p.get('estado_proceso') == 'vigente']

        # Ordenar por fecha
        licitaciones.sort(key=lambda x: x.get('cierre', ''), reverse=True)
        compras_menores.sort(key=lambda x: x.get('cierre', ''), reverse=True)

        # Guardar JSON
        datos_lic = {
            "metadata": {
                "tipo": "licitaciones",
                "total_procesos": len(licitaciones),
                "inversion_total": sum(p.get('monto', 0) for p in licitaciones),
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "vigentes",
                "cobertura": "Honduras - Todas las instituciones SICC",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "playwright-batch-processing-v7",
                "instituciones_procesadas": len(checkpoint['instituciones_procesadas']),
                "instituciones_fallidas": len(checkpoint['instituciones_fallidas'])
            },
            "procesos": licitaciones
        }

        datos_cm = {
            "metadata": {
                "tipo": "compras_menores",
                "total_procesos": len(compras_menores),
                "inversion_total": sum(p.get('monto', 0) for p in compras_menores),
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "vigentes",
                "cobertura": "Honduras - Todas las instituciones SICC",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "playwright-batch-processing-v7",
                "instituciones_procesadas": len(checkpoint['instituciones_procesadas']),
                "instituciones_fallidas": len(checkpoint['instituciones_fallidas'])
            },
            "procesos": compras_menores
        }

        with open('data/licitaciones.json', 'w', encoding='utf-8') as f:
            json.dump(datos_lic, f, indent=2, ensure_ascii=False)

        with open('data/compras-menores.json', 'w', encoding='utf-8') as f:
            json.dump(datos_cm, f, indent=2, ensure_ascii=False)

        print(f"✅ Licitaciones: {len(licitaciones)} procesos")
        print(f"✅ Compras menores: {len(compras_menores)} procesos")
        print(f"✅ Instituciones procesadas: {len(checkpoint['instituciones_procesadas'])}")
        print(f"⚠️  Instituciones fallidas: {len(checkpoint['instituciones_fallidas'])}\n")

        # Limpiar checkpoint si completó
        if len(checkpoint['instituciones_fallidas']) == 0:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
                print("🗑️  Checkpoint limpiado\n")

    def _eliminar_duplicados(self, procesos: List) -> List:
        """Elimina procesos duplicados por expediente"""
        vistos = set()
        unicos = []
        for p in procesos:
            exp = p.get('expediente', '').strip()
            if exp and exp not in vistos:
                vistos.add(exp)
                unicos.append(p)
        return unicos


if __name__ == "__main__":
    extractor = SICCExtractorV7()
    exito = extractor.extraer_lotes(tam_lote=50)
    sys.exit(0 if exito else 1)
