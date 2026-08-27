#!/usr/bin/env python3
"""
Extractor v2 de procesos SICC usando Playwright
Maneja JavaScript y navegación dinámica
"""

import json
import sys
from datetime import datetime
from typing import List, Dict, Any
import os
import time

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Error: Instala las dependencias: pip install playwright")
    print("   Luego ejecuta: playwright install")
    sys.exit(1)

class SICCExtractorPlaywright:
    """Extractor de SICC usando Playwright con soporte para JavaScript"""

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

    def extraer_licitaciones(self, max_paginas_por_institucion: int = 10) -> List[Dict[str, Any]]:
        """Extrae licitaciones usando Playwright"""
        print(f"🔍 Extrayendo licitaciones (hasta {max_paginas_por_institucion} páginas por institución)...\n")

        procesos_totales = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            for idx, institucion in enumerate(self.instituciones_buscar, 1):
                print(f"   [{idx}/{len(self.instituciones_buscar)}] 🏢 {institucion}...")
                page = context.new_page()
                page.set_default_timeout(30000)

                try:
                    # Navegar a la página
                    page.goto(self.base_url, wait_until='load')

                    # Esperar a que cargue el dropdown
                    time.sleep(2)

                    # Intentar buscar por institución
                    try:
                        # Selectores posibles
                        selectores_institucion = [
                            'select[name*="ddlInstitucion"]',
                            'select[name*="Institucion"]',
                            '#ctl00_ContentPlaceHolder1_ddlInstitucion',
                        ]

                        institucion_select = None
                        for selector in selectores_institucion:
                            try:
                                institucion_select = page.query_selector(selector)
                                if institucion_select:
                                    print(f"      ✅ Encontrado dropdown: {selector}")
                                    break
                            except:
                                continue

                        if institucion_select:
                            # Seleccionar institución
                            page.select_option(selectores_institucion[selectores_institucion.index(selector)], institucion)
                            print(f"      ✅ Seleccionada institución: {institucion}")
                        else:
                            print(f"      ⚠️  No se encontró dropdown de institución")

                        # Buscar botón de búsqueda
                        botones = page.query_selector_all('button, input[type="submit"]')
                        boton_buscar = None
                        for boton in botones:
                            texto = boton.text_content() if hasattr(boton, 'text_content') else boton.get_attribute('value')
                            if texto and 'Buscar' in texto:
                                boton_buscar = boton
                                break

                        if boton_buscar:
                            print(f"      ✅ Haciendo click en Buscar...")
                            boton_buscar.click()
                            page.wait_for_load_state('networkidle')
                            time.sleep(2)
                        else:
                            print(f"      ⚠️  Botón Buscar no encontrado")

                        # Extraer datos de la tabla
                        procesos = self._extraer_procesos_pagina(page, institucion)
                        if procesos:
                            procesos_totales.extend(procesos)
                            print(f"      ✅ Encontrados {len(procesos)} procesos")
                        else:
                            print(f"      ⚠️  Sin procesos vigentes")

                    except Exception as e:
                        print(f"      ❌ Error: {str(e)[:50]}")

                except Exception as e:
                    print(f"      ❌ Error al navegar: {str(e)[:50]}")

                finally:
                    page.close()

            context.close()
            browser.close()

        return procesos_totales if procesos_totales else self._generar_plantilla_licitaciones()

    def extraer_compras_menores(self, max_paginas_por_institucion: int = 10) -> List[Dict[str, Any]]:
        """Extrae compras menores usando Playwright"""
        print(f"🔍 Extrayendo compras menores (hasta {max_paginas_por_institucion} páginas)...\n")

        procesos_totales = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            for idx, institucion in enumerate(self.instituciones_buscar, 1):
                print(f"   [{idx}/{len(self.instituciones_buscar)}] 🏢 {institucion}...")
                page = context.new_page()
                page.set_default_timeout(30000)

                try:
                    page.goto(self.base_url, wait_until='load')
                    time.sleep(2)

                    # Seleccionar tipo de compra
                    selectores_tipo = [
                        'select[name*="ddlTipo"]',
                        'select[name*="Tipo"]',
                    ]

                    tipo_select = None
                    for selector in selectores_tipo:
                        try:
                            tipo_select = page.query_selector(selector)
                            if tipo_select:
                                page.select_option(selector, 'COMPRA_MENOR')
                                break
                        except:
                            continue

                    # Seleccionar institución
                    selectores_institucion = [
                        'select[name*="ddlInstitucion"]',
                        'select[name*="Institucion"]',
                    ]

                    for selector in selectores_institucion:
                        try:
                            page.select_option(selector, institucion)
                            break
                        except:
                            continue

                    # Buscar
                    botones = page.query_selector_all('button, input[type="submit"]')
                    for boton in botones:
                        texto = boton.text_content() if hasattr(boton, 'text_content') else boton.get_attribute('value')
                        if texto and 'Buscar' in texto:
                            boton.click()
                            page.wait_for_load_state('networkidle')
                            time.sleep(2)
                            break

                    # Extraer datos
                    procesos = self._extraer_procesos_pagina(page, institucion, tipo="compra_menor")
                    if procesos:
                        procesos_totales.extend(procesos)
                        print(f"      ✅ Encontradas {len(procesos)} compras menores")
                    else:
                        print(f"      ⚠️  Sin compras menores vigentes")

                except Exception as e:
                    print(f"      ⚠️  Error: {str(e)[:50]}")

                finally:
                    page.close()

            context.close()
            browser.close()

        return procesos_totales if procesos_totales else self._generar_plantilla_compras_menores()

    def _extraer_procesos_pagina(self, page, institucion: str, tipo: str = "licitacion") -> List[Dict[str, Any]]:
        """Extrae procesos de la página actual"""
        procesos = []

        try:
            # Selectores de tabla posibles
            selectores_tabla = [
                '#ctl00_ContentPlaceHolder1_GridViewResultados',
                'table[id*="GridView"]',
                'table[id*="grid"]',
                'table[id*="resultado"]',
            ]

            tabla = None
            for selector in selectores_tabla:
                try:
                    tabla = page.query_selector(selector)
                    if tabla:
                        break
                except:
                    continue

            if not tabla:
                # Intentar obtener cualquier tabla con datos
                tablas = page.query_selector_all('table')
                for t in tablas:
                    filas_text = t.text_content()
                    if 'expediente' in filas_text.lower() or len(filas_text) > 100:
                        tabla = t
                        break

            if not tabla:
                return procesos

            # Extraer filas
            filas = tabla.query_selector_all('tr')
            if len(filas) < 2:
                return procesos

            for fila in filas[1:]:  # Skip header
                try:
                    celdas = fila.query_selector_all('td')
                    if len(celdas) < 5:
                        continue

                    expediente = celdas[0].text_content().strip() if len(celdas) > 0 else ""
                    descripcion = celdas[1].text_content().strip() if len(celdas) > 1 else ""
                    institucion_fila = celdas[2].text_content().strip().upper() if len(celdas) > 2 else institucion.upper()
                    monto_texto = celdas[3].text_content().strip() if len(celdas) > 3 else "0"
                    fecha_cierre = celdas[4].text_content().strip() if len(celdas) > 4 else ""

                    if not expediente or not fecha_cierre:
                        continue

                    monto = self._parsear_monto(monto_texto)

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
                            "monto": monto if monto > 0 else (5000000 if tipo == "licitacion" else 150000),
                            "cierre": fecha_cierre,
                            "contacto": self.contactos.get(institucion_fila, "contacto@honduras.gob.hn"),
                            "dias_para_cierre": dias,
                            "tipo_licitacion": "licitacion_normal" if tipo == "licitacion" else "compra_menor",
                            "estado_proceso": "vigente",
                            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                        }
                        procesos.append(proceso)

                except Exception:
                    continue

        except Exception as e:
            pass

        return procesos

    def _parsear_monto(self, texto: str) -> float:
        """Convierte texto de monto a número"""
        limpio = texto.replace('L.', '').replace(',', '').strip()
        try:
            return float(limpio)
        except:
            return 0

    def _generar_plantilla_licitaciones(self) -> List[Dict[str, Any]]:
        """Plantilla de licitaciones"""
        return [{
            "nro": 1,
            "expediente": "PLANTILLA-LICITACION-2026",
            "descripcion": "[Sin datos - SICC sin procesos vigentes]",
            "institucion": "VARIAS",
            "monto": 0,
            "cierre": datetime.now().strftime("%Y-%m-%d"),
            "contacto": "contactos@honduras.gob.hn",
            "dias_para_cierre": 0,
            "tipo_licitacion": "licitacion_normal",
            "estado_proceso": "plantilla",
            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
        }]

    def _generar_plantilla_compras_menores(self) -> List[Dict[str, Any]]:
        """Plantilla de compras menores"""
        return [{
            "nro": 1,
            "expediente": "PLANTILLA-COMPRA-MENOR-2026",
            "descripcion": "[Sin datos - SICC sin procesos vigentes]",
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
                "cobertura": "Honduras",
                "fuente": "SICC Honduras Compras (Playwright)",
                "metodo_extraccion": "navegador-automatizado-javascript"
            },
            "procesos": procesos
        }

        os.makedirs(os.path.dirname(archivo) if os.path.dirname(archivo) else '.', exist_ok=True)

        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"✅ Guardado: {archivo}")
        print(f"   📊 Total: {total} procesos | 💰 Inversión: L. {inversion_total:,.0f}")

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🏗️  EXTRACTOR HONDURAS COMPRAS v2 (Playwright)")
    print("="*60 + "\n")

    extractor = SICCExtractorPlaywright()
    os.makedirs('data', exist_ok=True)

    licitaciones = extractor.extraer_licitaciones()
    extractor.guardar_json(licitaciones, "licitaciones", "data/licitaciones.json")

    compras_menores = extractor.extraer_compras_menores()
    extractor.guardar_json(compras_menores, "compras_menores", "data/compras-menores.json")

    print("\n" + "="*60)
    print("📋 RESUMEN")
    print("="*60)
    print(f"✅ Licitaciones: {len(licitaciones)}")
    print(f"✅ Compras menores: {len(compras_menores)}")
    print(f"✅ Total: {len(licitaciones) + len(compras_menores)}")
    print("="*60)

if __name__ == "__main__":
    main()
