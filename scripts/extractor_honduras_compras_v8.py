#!/usr/bin/env python3
"""
Extractor v8 - Discovery + Detail con adaptación dinámica
Fase 1: Descubre instituciones activas (búsqueda global, sin dropdown)
Fase 2: Extrae detalles solo de instituciones activas
"""

import json
import sys
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set
import os

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Error: pip install playwright")
    sys.exit(1)

class SICCExtractorV8:
    """Extractor v8 - Discovery dinámico sin dropdown"""

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
        self.estado_file = "scripts/.extractor_v8_estado.json"

    def _cargar_estado(self) -> Dict[str, Any]:
        """Carga estado anterior"""
        if os.path.exists(self.estado_file):
            try:
                with open(self.estado_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "instituciones_activas": {},
            "procesos_totales": 0,
            "ultima_actualizacion": "",
            "cambios": []
        }

    def _guardar_estado(self, estado: Dict[str, Any]):
        """Guarda estado"""
        with open(self.estado_file, 'w', encoding='utf-8') as f:
            json.dump(estado, f, indent=2, default=str, ensure_ascii=False)

    def _es_construccion(self, texto: str) -> bool:
        """Verifica si menciona construcción/ingeniería"""
        texto_lower = texto.lower()
        return any(palabra in texto_lower for palabra in self.palabras_construccion)

    def fase_1_discovery(self, page) -> Dict[str, int]:
        """FASE 1: Descubre instituciones activas con búsqueda global"""
        print("\n" + "=" * 70)
        print("FASE 1: DISCOVERY - Identificando instituciones activas")
        print("=" * 70 + "\n")

        instituciones_activas = {}

        try:
            print("📍 Navegando a SICC (sin filtro institución)...\n")
            page.goto(self.base_url, wait_until='load', timeout=30000)
            time.sleep(1)

            print("🔄 Buscando TODOS los procesos (construcción/ingeniería 2026+)...\n")

            # No seleccionar institución = búsqueda global
            # Seleccionar ambos tipos
            page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipos', 'licitacion')
            time.sleep(0.5)

            ahora = datetime.now()
            procesos_encontrados = 0
            pagina = 1

            while pagina <= 100:
                try:
                    filas = page.query_selector_all('table[id*="gvResultados"] tbody tr')
                    if not filas:
                        if pagina == 1:
                            print("   ⚠️  No hay resultados")
                        break

                    for fila in filas:
                        try:
                            celdas = fila.query_selector_all('td')
                            if len(celdas) < 8:
                                continue

                            expediente = celdas[1].text_content().strip()
                            descripcion = celdas[2].text_content().strip()
                            institucion_texto = celdas[7].text_content().strip()  # Columna institución
                            cierre_text = celdas[5].text_content().strip()

                            # Filtrar construcción
                            if not self._es_construccion(f"{expediente} {descripcion}"):
                                continue

                            # Filtrar fecha 2026+
                            try:
                                fecha_cierre = datetime.strptime(cierre_text, "%d/%m/%Y")
                                if fecha_cierre.year < 2026 or fecha_cierre < ahora:
                                    continue
                            except:
                                continue

                            # Registrar institución
                            institucion_limpia = institucion_texto.split('-')[0].strip() if '-' in institucion_texto else institucion_texto.strip()

                            if institucion_limpia not in instituciones_activas:
                                instituciones_activas[institucion_limpia] = 0

                            instituciones_activas[institucion_limpia] += 1
                            procesos_encontrados += 1

                        except Exception:
                            continue

                    # Siguiente página
                    try:
                        btn_siguiente = page.query_selector('a[id*="lnkSiguiente"]')
                        if not btn_siguiente or 'disabled' in btn_siguiente.get_attribute('class', ''):
                            break

                        btn_siguiente.click()
                        time.sleep(0.3)
                        pagina += 1

                    except:
                        break

                except Exception as e:
                    print(f"   ⚠️  Error en página {pagina}: {e}")
                    break

            print(f"\n✅ Discovery completo:")
            print(f"   📊 Procesos encontrados: {procesos_encontrados}")
            print(f"   🏢 Instituciones activas: {len(instituciones_activas)}\n")

            # Ordenar por cantidad de procesos
            instituciones_ordenadas = sorted(instituciones_activas.items(), key=lambda x: x[1], reverse=True)

            print("   TOP 20 instituciones por actividad:")
            for i, (inst, count) in enumerate(instituciones_ordenadas[:20], 1):
                print(f"   {i:2d}. {inst:40s} ({count} procesos)")

            return dict(instituciones_ordenadas)

        except Exception as e:
            print(f"❌ Error en discovery: {e}")
            return {}

    def fase_2_detail(self, page, instituciones: Dict[str, int]) -> tuple:
        """FASE 2: Extrae detalles de instituciones activas"""
        print("\n" + "=" * 70)
        print("FASE 2: DETAIL - Extrayendo procesos de instituciones activas")
        print("=" * 70 + "\n")

        licitaciones = []
        compras_menores = []
        ahora = datetime.now()

        # Procesar top 30 instituciones
        instituciones_a_procesar = list(instituciones.items())[:30]

        print(f"📋 Procesando {len(instituciones_a_procesar)} instituciones principales\n")

        for idx, (inst_nombre, count_estimado) in enumerate(instituciones_a_procesar, 1):
            try:
                print(f"   {idx:2d}. {inst_nombre:40s} ({count_estimado} est.)", end=" ", flush=True)

                # Obtener ID de institución del dropdown
                page.goto(self.base_url, wait_until='load', timeout=30000)
                time.sleep(0.3)

                opciones = page.query_selector_all('#ctl00_cphCuerpo_wpParametros_ddlEntidades option')
                inst_id = None

                for opcion in opciones:
                    try:
                        if inst_nombre.lower() in opcion.text_content().lower():
                            inst_id = opcion.get_attribute('value')
                            break
                    except:
                        continue

                if not inst_id:
                    print("✗ (no encontrada)")
                    continue

                # Procesar licitaciones
                try:
                    page.goto(self.base_url, wait_until='load', timeout=30000)
                    time.sleep(0.3)
                    page.select_option('#ctl00_cphCuerpo_wpParametros_ddlEntidades', inst_id)
                    time.sleep(0.5)
                    page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipos', 'licitacion')
                    time.sleep(0.5)

                    procs_lic = self._extraer_paginas(page, "licitacion", inst_nombre, ahora)
                    licitaciones.extend(procs_lic)

                    # Procesar compras menores
                    page.goto(self.base_url, wait_until='load', timeout=30000)
                    time.sleep(0.3)
                    page.select_option('#ctl00_cphCuerpo_wpParametros_ddlEntidades', inst_id)
                    time.sleep(0.5)
                    page.select_option('#ctl00_cphCuerpo_wpParametros_ddlTipos', 'compra_menor')
                    time.sleep(0.5)

                    procs_cm = self._extraer_paginas(page, "compra_menor", inst_nombre, ahora)
                    compras_menores.extend(procs_cm)

                    print(f"✓ ({len(procs_lic)}L + {len(procs_cm)}C)")

                except Exception as e:
                    print(f"✗ ({str(e)[:30]})")
                    continue

            except Exception as e:
                print(f"✗ Error: {e}")
                continue

        return licitaciones, compras_menores

    def _extraer_paginas(self, page, tipo: str, institucion: str, ahora: datetime) -> List[Dict]:
        """Extrae todas las páginas de un tipo"""
        procesos = []
        pagina = 1

        while pagina <= 20:
            try:
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

                        if not self._es_construccion(f"{expediente} {modalidad} {etapa}"):
                            continue

                        try:
                            fecha_cierre = datetime.strptime(cierre_text, "%d/%m/%Y")
                            if fecha_cierre.year < 2026 or fecha_cierre < ahora:
                                continue
                        except:
                            continue

                        dias = (fecha_cierre - ahora).days

                        monto = 0
                        try:
                            monto = int(''.join(filter(str.isdigit, monto_text)))
                        except:
                            pass

                        link_elem = celdas[0].query_selector('a')
                        link = link_elem.get_attribute('href') if link_elem else ""

                        proceso = {
                            "expediente": expediente,
                            "descripcion": descripcion,
                            "institucion": institucion,
                            "modalidad": modalidad,
                            "etapa": etapa,
                            "cierre": cierre_text,
                            "monto": monto,
                            "dias_para_cierre": dias,
                            "tipo_licitacion": tipo,
                            "link": link,
                            "contacto": self.contactos.get(institucion.split()[0].upper(), "no-disponible@hnd.gob.hn"),
                            "estado_proceso": "vigente",
                            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                        }

                        procesos.append(proceso)

                    except Exception:
                        continue

                # Siguiente
                try:
                    btn_siguiente = page.query_selector('a[id*="lnkSiguiente"]')
                    if not btn_siguiente or 'disabled' in btn_siguiente.get_attribute('class', ''):
                        break

                    btn_siguiente.click()
                    time.sleep(0.3)
                    pagina += 1

                except:
                    break

            except Exception:
                break

        return procesos

    def consolidar(self, licitaciones: List, compras_menores: List, instituciones: Dict):
        """Consolida datos finales"""
        print("\n" + "=" * 70)
        print("CONSOLIDANDO DATOS")
        print("=" * 70 + "\n")

        # Eliminar duplicados
        licitaciones = self._eliminar_duplicados(licitaciones)
        compras_menores = self._eliminar_duplicados(compras_menores)

        # Ordenar
        licitaciones.sort(key=lambda x: x.get('cierre', ''), reverse=True)
        compras_menores.sort(key=lambda x: x.get('cierre', ''), reverse=True)

        # JSON licitaciones
        datos_lic = {
            "metadata": {
                "tipo": "licitaciones",
                "total_procesos": len(licitaciones),
                "inversion_total": sum(p.get('monto', 0) for p in licitaciones),
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "vigentes",
                "cobertura": "Honduras - Instituciones activas descubiertas dinámicamente",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "discovery-detail-v8",
                "instituciones_analizadas": len(instituciones),
                "instituciones_procesadas": len(set(p.get('institucion') for p in licitaciones))
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
                "cobertura": "Honduras - Instituciones activas descubiertas dinámicamente",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "discovery-detail-v8",
                "instituciones_analizadas": len(instituciones),
                "instituciones_procesadas": len(set(p.get('institucion') for p in compras_menores))
            },
            "procesos": compras_menores
        }

        with open('data/licitaciones.json', 'w', encoding='utf-8') as f:
            json.dump(datos_lic, f, indent=2, ensure_ascii=False)

        with open('data/compras-menores.json', 'w', encoding='utf-8') as f:
            json.dump(datos_cm, f, indent=2, ensure_ascii=False)

        print(f"✅ Licitaciones: {len(licitaciones)} procesos")
        print(f"✅ Compras menores: {len(compras_menores)} procesos")
        print(f"✅ Total: {len(licitaciones) + len(compras_menores)} procesos vigentes\n")

        # Actualizar estado
        estado = {
            "instituciones_activas": instituciones,
            "procesos_totales": len(licitaciones) + len(compras_menores),
            "ultima_actualizacion": datetime.now().isoformat(),
            "cambios": []
        }
        self._guardar_estado(estado)

        # Limpiar checkpoint v7 si existe
        if os.path.exists("scripts/.extractor_v7_checkpoint.json"):
            os.remove("scripts/.extractor_v7_checkpoint.json")

    def _eliminar_duplicados(self, procesos: List) -> List:
        """Elimina duplicados"""
        vistos = set()
        unicos = []
        for p in procesos:
            exp = p.get('expediente', '').strip()
            if exp and exp not in vistos:
                vistos.add(exp)
                unicos.append(p)
        return unicos

    def ejecutar(self):
        """Ejecuta ambas fases"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(30000)

                # Fase 1: Discovery
                instituciones = self.fase_1_discovery(page)

                if not instituciones:
                    print("❌ No se descubrieron instituciones activas")
                    browser.close()
                    return False

                # Fase 2: Detail
                licitaciones, compras_menores = self.fase_2_detail(page, instituciones)

                # Consolidar
                self.consolidar(licitaciones, compras_menores, instituciones)

                browser.close()
                return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False


if __name__ == "__main__":
    extractor = SICCExtractorV8()
    exito = extractor.ejecutar()
    sys.exit(0 if exito else 1)
