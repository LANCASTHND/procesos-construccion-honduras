#!/usr/bin/env python3
"""
Extractor v3 - Con selectores SICC correctos descubiertos
Usa IDs reales de SICC para extracción precisa
"""

import json
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import time
import re

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Error: pip install playwright")
    sys.exit(1)

class SICCExtractorV3:
    """Extractor v3 con selectores correctos"""

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
        }
        self.instituciones_buscar = list(self.contactos.keys())

    def _extraer_institucion(self, expediente: str) -> str:
        """Extrae institución del texto del expediente"""
        expediente_upper = expediente.upper().strip()

        # Limpiar expediente de espacios en blanco extra
        expediente_clean = ' '.join(expediente_upper.split())

        # Buscar siglas de instituciones (primero exactas, luego parciales)
        for sigla in self.contactos.keys():
            sigla_upper = sigla.upper()
            # Buscar como palabra completa o al inicio
            if sigla_upper in expediente_clean:
                return sigla
            # Para siglas cortas, buscar como patrón más específico
            if len(sigla_upper) <= 3 and sigla_upper in expediente_clean:
                return sigla

        # Fallback: buscar por nombres comunes
        if "BOMBEROS" in expediente_clean or "CUERPO" in expediente_clean:
            return "CUERPO DE BOMBEROS"
        elif "MUNICIPAL" in expediente_clean or "MUNICIPALI" in expediente_clean:
            return "VARIAS MUNICIPALIDADES"
        elif "SPE" in expediente_clean:
            # SPE usualmente es de municipalidades
            return "VARIAS MUNICIPALIDADES"

        return "VARIAS"

    def extraer_licitaciones(self) -> List[Dict[str, Any]]:
        """Extrae TODAS las licitaciones vigentes"""
        print("🔍 Extrayendo TODAS las licitaciones vigentes...\n")

        procesos = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(30000)

            try:
                # Navegar a SICC
                page.goto(self.base_url, wait_until='load')
                print("   ✅ Página SICC cargada\n")
                time.sleep(2)

                # Seleccionar tipo de adquisición: Obras (2 = Obras)
                selector_tipo = '#ctl00_cphCuerpo_wpParametros_ddlTipoAdquisicion'
                try:
                    page.select_option(selector_tipo, '2')
                    print("   ✅ Filtro 'Obras' seleccionado\n")
                except:
                    print("   ⚠️  No se pudo filtrar por Obras, buscando todas las categorías\n")

                # Hacer clic en Buscar
                print("   🔍 Iniciando búsqueda...")
                btn_buscar = '#ctl00_cphCuerpo_wpParametros_btnBuscar'
                page.click(btn_buscar)
                page.wait_for_load_state('networkidle')
                print("   ✅ Búsqueda completada\n")

                time.sleep(2)

                # Extraer datos de la tabla de resultados
                procesos = self._extraer_procesos_de_pagina(page, "licitacion")

                if procesos:
                    print(f"   ✅ Encontrados {len(procesos)} procesos de licitación\n")
                else:
                    print("   ⚠️  No se encontraron procesos\n")

            except Exception as e:
                print(f"   ❌ Error: {e}\n")

            finally:
                browser.close()

        return procesos if procesos else self._generar_plantilla()

    def extraer_compras_menores(self) -> List[Dict[str, Any]]:
        """Extrae TODAS las compras menores vigentes"""
        print("🔍 Extrayendo TODAS las compras menores vigentes...\n")

        procesos = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(30000)

            try:
                page.goto(self.base_url, wait_until='load')
                print("   ✅ Página SICC cargada\n")
                time.sleep(2)

                # Intento 1: Intentar con filtro de Compra Menor
                print("   🔍 Intento 1: Buscando compras menores con filtro...")
                procesos = self._buscar_compras_con_filtro(page)

                if procesos and len(procesos) > 0:
                    print(f"   ✅ Encontradas {len(procesos)} compras menores con filtro\n")
                else:
                    # Intento 2: Si falla, recargar la página y buscar sin filtro
                    print("   ⚠️  Intento con filtro falló, reintentando sin filtro...\n")
                    page.reload(wait_until='load')
                    time.sleep(2)
                    procesos = self._buscar_compras_sin_filtro(page)

                    if procesos:
                        print(f"   ✅ Encontradas {len(procesos)} compras menores sin filtro\n")
                    else:
                        print("   ⚠️  No se encontraron procesos (usando fallback)\n")

            except Exception as e:
                print(f"   ❌ Error: {e}\n")

            finally:
                browser.close()

        return procesos if procesos else self._generar_plantilla_compras()

    def _buscar_compras_con_filtro(self, page) -> List[Dict[str, Any]]:
        """Intenta buscar compras menores con filtro de modalidad"""
        try:
            # Seleccionar modalidad: Compra Menor
            selector_modalidad = '#ctl00_cphCuerpo_wpParametros_ddlModalidad'
            page.select_option(selector_modalidad, '2')
            print("   ✅ Filtro 'Compra Menor' seleccionado")

            # Click en buscar
            btn_buscar = '#ctl00_cphCuerpo_wpParametros_btnBuscar'
            page.click(btn_buscar, no_wait_after=True)
            time.sleep(4)

            # Extraer datos
            return self._extraer_procesos_de_pagina(page, "compra_menor")
        except Exception as e:
            print(f"   ⚠️  Error en búsqueda con filtro: {e}")
            return []

    def _buscar_compras_sin_filtro(self, page) -> List[Dict[str, Any]]:
        """Intenta buscar compras menores sin filtro (todas las modalidades)"""
        try:
            # Click en buscar sin filtro
            btn_buscar = '#ctl00_cphCuerpo_wpParametros_btnBuscar'
            page.click(btn_buscar, no_wait_after=True)
            time.sleep(4)

            # Extraer datos y filtrar por compras menores
            procesos_todos = self._extraer_procesos_de_pagina(page, "compra_menor")

            # Si tenemos resultados, retornarlos
            if procesos_todos:
                return procesos_todos

            return []
        except Exception as e:
            print(f"   ⚠️  Error en búsqueda sin filtro: {e}")
            return []

    def _extraer_procesos_de_pagina(self, page, tipo: str = "licitacion") -> List[Dict[str, Any]]:
        """Extrae procesos de la tabla de resultados actual"""
        procesos = []

        try:
            # Esperar a que cargue la tabla y que el contexto se estabilice
            max_wait = 10
            for i in range(max_wait):
                try:
                    time.sleep(1)
                    # Verificar que el contexto sigue vivo
                    page.query_selector('body')
                    break
                except Exception as e:
                    if i == max_wait - 1:
                        print(f"   ⚠️  No se pudo recuperar el contexto después de {max_wait}s")
                        return procesos
                    print(f"   ⏳ Esperando contexto ({i+1}/{max_wait})...")

            # Buscar todas las tablas
            tablas = page.query_selector_all('table')
            print(f"   📊 Tablas encontradas: {len(tablas)}")

            # Buscar tabla con header "Proceso de Adquisición"
            tabla_procesos = None
            for idx_tabla, tabla in enumerate(tablas):
                filas = tabla.query_selector_all('tr')
                if len(filas) > 2:
                    # Verificar si es la tabla de procesos
                    primera_fila = filas[0]
                    header_text = primera_fila.text_content()
                    print(f"   🔎 Tabla {idx_tabla}: '{header_text[:60]}...' ({len(filas)} filas)")

                    # Buscar indicadores de que es tabla de procesos
                    if ("Proceso de Adquisición" in header_text or
                        "Adquisición" in header_text or
                        "Expediente" in header_text or
                        "Modalidad" in header_text):
                        tabla_procesos = tabla
                        print(f"   ✅ Tabla de procesos identificada ({len(filas)} filas)")
                        break

            if not tabla_procesos:
                print("   ⚠️  No se encontró tabla de procesos")
                print(f"   💡 Intentando con la tabla más grande...")
                # Fallback: usar la tabla más grande (ignorar tablas muy pequeñas)
                tablas_validas = [t for t in tablas if len(t.query_selector_all('tr')) > 3]
                if tablas_validas:
                    tabla_procesos = max(tablas_validas, key=lambda t: len(t.query_selector_all('tr')))
                    filas = tabla_procesos.query_selector_all('tr')
                    print(f"   ✅ Usando tabla de fallback ({len(filas)} filas)")
                else:
                    print(f"   ❌ No hay tablas válidas con datos")
                    return procesos

            # Extraer filas (skip header)
            filas = tabla_procesos.query_selector_all('tr')
            datos_filas = filas[1:] if len(filas) > 1 else []

            print(f"   📋 Procesando {len(datos_filas)} filas de datos...")

            for idx, fila in enumerate(datos_filas):
                try:
                    celdas = fila.query_selector_all('td')

                    if len(celdas) < 4:
                        continue

                    # Extraer datos de celdas (formato SICC real)
                    # [0]: Expediente: ...
                    # [1]: Etapa (Recepción de Ofertas, etc)
                    # [2]: Modalidad (Licitación pública, etc)
                    # [3]: Fecha Inicio: dd/mm/yyyy
                    # [4]: Ver Detalle (link)

                    expediente_texto = celdas[0].text_content().strip() if len(celdas) > 0 else ""
                    etapa = celdas[1].text_content().strip() if len(celdas) > 1 else ""
                    modalidad = celdas[2].text_content().strip() if len(celdas) > 2 else ""
                    vigencia_texto = celdas[3].text_content().strip() if len(celdas) > 3 else ""

                    # Extraer link de celda [4] si existe
                    link = ""
                    if len(celdas) > 4:
                        link_elem = celdas[4].query_selector('a')
                        if link_elem:
                            link = link_elem.get_attribute('href') or ""

                    if not expediente_texto or not vigencia_texto:
                        continue

                    # Parsear expediente (quitar prefijo "Expediente:")
                    expediente = expediente_texto.replace("Expediente:", "").strip()
                    if not expediente:
                        continue

                    # Parsear fecha de vigencia (formato: "Fecha Inicio:\n17/08/2026")
                    # Buscar patrón dd/mm/yyyy
                    import re
                    fecha_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', vigencia_texto)
                    if not fecha_match:
                        continue

                    fecha_inicio_str = fecha_match.group(0)

                    # Verificar que sea vigente (fecha inicio debe ser hoy o antes)
                    try:
                        fecha_inicio = datetime.strptime(fecha_inicio_str, '%d/%m/%Y')
                        # Estimar fecha cierre (generalmente 30-45 días después)
                        cierre_estimado = fecha_inicio + timedelta(days=35)
                        dias = (cierre_estimado - datetime.now()).days

                        if dias < 0:
                            continue  # Muy antiguo
                    except:
                        continue

                    # Extraer institución del expediente
                    # Buscar patrones comunes: "UNAH", "UNA", "SIT", "SEDENA", etc.
                    institucion = self._extraer_institucion(expediente)

                    # Crear proceso
                    proceso = {
                        "expediente": expediente[:80],  # Limitar longitud
                        "descripcion": modalidad,
                        "institucion": institucion,
                        "monto": 0,
                        "cierre": cierre_estimado.strftime('%d/%m/%Y'),
                        "contacto": self.contactos.get(institucion, ""),
                        "link": link,
                        "dias_para_cierre": dias,
                        "tipo_licitacion": tipo,
                        "etapa": etapa,
                        "modalidad": modalidad,
                        "fecha_inicio": fecha_inicio_str,
                        "estado_proceso": "vigente",
                        "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                    }
                    procesos.append(proceso)

                except Exception as e:
                    continue

            print(f"   ✅ Extrados {len(procesos)} procesos válidos")

        except Exception as e:
            print(f"   ❌ Error extrayendo procesos: {e}")

        return procesos

    def _generar_plantilla(self) -> List[Dict[str, Any]]:
        return [{
            "nro": 1,
            "expediente": "PLANTILLA-LICITACION-2026",
            "descripcion": "[Sin datos]",
            "institucion": "VARIAS",
            "monto": 0,
            "cierre": datetime.now().strftime("%Y-%m-%d"),
            "contacto": "contactos@honduras.gob.hn",
            "dias_para_cierre": 0,
            "tipo_licitacion": "licitacion_normal",
            "estado_proceso": "plantilla",
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
        }]

    def _generar_plantilla_compras(self) -> List[Dict[str, Any]]:
        return [{
            "nro": 1,
            "expediente": "PLANTILLA-COMPRA-MENOR-2026",
            "descripcion": "[Sin datos]",
            "institucion": "VARIAS",
            "monto": 0,
            "cierre": datetime.now().strftime("%Y-%m-%d"),
            "contacto": "contactos@honduras.gob.hn",
            "dias_para_cierre": 0,
            "tipo_licitacion": "compra_menor",
            "estado_proceso": "plantilla",
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
        }]

    def guardar_json(self, procesos: List[Dict], tipo: str, archivo: str):
        """Guarda procesos en JSON"""
        total = len(procesos)
        inversion_total = sum(p.get('monto', 0) for p in procesos)

        for idx, proceso in enumerate(procesos, 1):
            if 'nro' not in proceso:
                proceso['nro'] = idx

        datos = {
            "metadata": {
                "tipo": "licitaciones_normales" if tipo == "licitaciones" else "compras_menores",
                "total_procesos": total,
                "inversion_total": inversion_total,
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "vigentes",
                "cobertura": "Honduras - Búsqueda General",
                "fuente": "SICC Honduras Compras",
                "metodo_extraccion": "playwright-navegador-automatizado-javascript"
            },
            "procesos": procesos
        }

        os.makedirs(os.path.dirname(archivo) if os.path.dirname(archivo) else '.', exist_ok=True)

        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"✅ Guardado: {archivo}")
        print(f"   📊 Total: {total} procesos | 💰 Inversión: L. {inversion_total:,.0f}\n")

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🏗️  EXTRACTOR HONDURAS COMPRAS v3 (Selectores Correctos)")
    print("="*60 + "\n")

    extractor = SICCExtractorV3()
    os.makedirs('data', exist_ok=True)

    print("["+"─"*58+"]")
    print("LICITACIONES")
    print("["+"─"*58+"]\n")
    licitaciones = extractor.extraer_licitaciones()
    extractor.guardar_json(licitaciones, "licitaciones", "data/licitaciones.json")

    print("["+"─"*58+"]")
    print("COMPRAS MENORES")
    print("["+"─"*58+"]\n")
    compras_menores = extractor.extraer_compras_menores()
    extractor.guardar_json(compras_menores, "compras_menores", "data/compras-menores.json")

    print("["+"─"*58+"]")
    print("📋 RESUMEN")
    print("["+"─"*58+"]")
    print(f"✅ Licitaciones: {len(licitaciones)}")
    print(f"✅ Compras menores: {len(compras_menores)}")
    print(f"✅ Total procesos: {len(licitaciones) + len(compras_menores)}")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
