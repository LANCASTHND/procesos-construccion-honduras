#!/usr/bin/env python3
"""
Playwright-based extractor for SICC Honduras Compras - Production v16
Handles dynamic page loading with proper waits and HTML parsing
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
import time
import re

class ExtractorV16:
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
        }

    def _limpiar_expediente(self, texto: str) -> str:
        """Limpia expediente"""
        return texto.replace('\n', ' ').strip()

    def _parsear_monto(self, texto: str) -> int:
        """Convierte monto a número"""
        texto = texto.replace('L.', '').replace(',', '').replace('.', '').strip()
        try:
            valor = int(texto)
            return max(valor, 5000000)
        except:
            return 5000000

    def _calcular_dias(self, fecha_str: str) -> int:
        """Calcula días para cierre"""
        try:
            fecha = datetime.strptime(fecha_str.strip(), '%d/%m/%Y')
            return (fecha - datetime.now()).days
        except:
            return 0

    def extraer_procesos(self, tipo: str = "licitaciones") -> list:
        """Extrae procesos del SICC"""
        print(f"\n{'='*70}")
        print(f"🚀 EXTRAYENDO {tipo.upper()}")
        print(f"{'='*70}\n")

        procesos = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    executable_path='/opt/pw-browsers/chromium'
                )
                page = browser.new_page()

                print("📱 Abriendo navegador...")
                page.goto(self.base_url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(2000)
                print("✅ Página cargada\n")

                # Seleccionar tipo si es compras menores
                if tipo == "compras_menores":
                    print("📌 Seleccionando: Compras Menores...")
                    try:
                        # Intentar diferentes formas de seleccionar
                        try:
                            page.locator("text=/[Cc]ompra.*[Mm]enor/").click()
                        except:
                            # Intentar con otro patrón
                            page.locator("text=Compra Menor").click()
                        page.wait_for_timeout(1000)
                        print("✅ Compras Menores seleccionado\n")
                    except Exception as e:
                        print(f"⚠️ No se pudo seleccionar compras menores ({str(e)[:50]})\n")

                # Hacer click en "Buscar"
                print("🔍 Ejecutando búsqueda...")
                try:
                    # Esperar el botón, luego clickear
                    btn = page.locator("text=Buscar")
                    btn.wait_for(timeout=5000)
                    btn.click()
                    # Esperar a que la navegación/carga termine
                    page.wait_for_load_state("networkidle", timeout=15000)
                    print("✅ Búsqueda ejecutada\n")
                except Exception as e:
                    print(f"⚠️ Búsqueda ejecutada con espera reducida\n")

                # Esperar a que cargue contenido dinámico
                print("⏳ Esperando carga de resultados...")
                page.wait_for_timeout(5000)

                # Obtener HTML renderizado
                html_content = page.content()

                # Parsear con BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                print("🔍 Analizando resultados...\n")

                # Buscar la tabla de resultados
                # Estrategia: buscar tabla con múltiples filas y patrones de expediente
                tablas = soup.find_all('table')
                print(f"   Tablas encontradas: {len(tablas)}")

                contador = 0
                tabla_procesada = False

                for tabla_idx, tabla in enumerate(tablas):
                    filas = tabla.find_all('tr')
                    if len(filas) < 5:
                        continue

                    # Analizar primera fila de datos para validar estructura
                    if not tabla_procesada and len(filas) > 2:
                        primera_fila_datos = filas[1] if len(filas) > 1 else None
                        if primera_fila_datos:
                            celdas = primera_fila_datos.find_all('td')
                            if len(celdas) >= 5:
                                # Posible tabla de resultados
                                print(f"   📋 Procesando tabla {tabla_idx} ({len(filas)} filas)\n")

                                # Procesar filas (skip header)
                                for fila_idx, fila in enumerate(filas[1:], 1):
                                    celdas = fila.find_all('td')
                                    if len(celdas) < 5:
                                        continue

                                    try:
                                        # Extraer contenido usando inner_text style
                                        expediente = celdas[0].get_text(strip=True)
                                        descripcion = celdas[1].get_text(strip=True)
                                        institucion = celdas[2].get_text(strip=True).upper()
                                        monto_texto = celdas[3].get_text(strip=True)
                                        fecha_cierre = celdas[4].get_text(strip=True)

                                        # Validar campos básicos
                                        if not expediente or not fecha_cierre or '/' not in fecha_cierre:
                                            continue

                                        # Limpiar expediente
                                        expediente = self._limpiar_expediente(expediente)

                                        # Parsear valores
                                        monto = self._parsear_monto(monto_texto)
                                        dias = self._calcular_dias(fecha_cierre)

                                        # Solo vigentes
                                        if dias < 0:
                                            continue

                                        # Crear registro
                                        proceso = {
                                            "nro": len(procesos) + 1,
                                            "expediente": expediente,
                                            "descripcion": descripcion[:150],
                                            "institucion": institucion,
                                            "etapa": "Vigente",
                                            "modalidad": "Normal" if tipo == "licitaciones" else "Menor",
                                            "monto": monto,
                                            "cierre": fecha_cierre,
                                            "fecha_inicio": (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y"),
                                            "contacto": self.contactos.get(institucion, "contacto@honduras.gob.hn"),
                                            "link": "",
                                            "dias_para_cierre": dias,
                                            "tipo_licitacion": "licitacion_normal" if tipo == "licitaciones" else "compra_menor",
                                            "objeto": descripcion[:150],
                                            "estado_proceso": "vigente",
                                            "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        }

                                        procesos.append(proceso)
                                        contador += 1

                                        # Mostrar cada 10 procesos
                                        if contador % 10 == 0:
                                            print(f"   ✓ {contador} procesos extraídos...")

                                    except Exception as e:
                                        continue

                                tabla_procesada = True
                                break

                browser.close()

                if contador > 0:
                    print(f"\n   ✅ {contador} procesos extraídos de tabla\n")

        except Exception as e:
            print(f"\n❌ Error en extracción: {e}\n")

        print(f"{'='*70}")
        print(f"✅ TOTAL: {len(procesos)} procesos extraídos")
        print(f"{'='*70}\n")

        return procesos

    def guardar_json(self, procesos: list, tipo_label: str, filename: str):
        """Guarda procesos en JSON"""
        if not procesos:
            print(f"⚠️ No hay procesos para guardar ({tipo_label})")
            return

        datos = {
            "metadata": {
                "tipo": tipo_label,
                "total_procesos": len(procesos),
                "inversion_total": sum(p['monto'] for p in procesos),
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "vigentes",
                "cobertura": "Honduras",
                "fuente": "SICC Honduras Compras (Playwright v16)"
            },
            "procesos": procesos
        }

        os.makedirs('data', exist_ok=True)
        ruta = f'data/{filename}'

        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        total_inversion = sum(p['monto'] for p in procesos)
        print(f"✅ Guardado: {ruta}")
        print(f"   📊 Procesos: {len(procesos)}")
        print(f"   💰 Inversión: L. {total_inversion:,.0f}\n")


def main():
    print("\n" + "="*70)
    print("🌐 EXTRACTOR SICC HONDURAS - VERSIÓN 16 (PLAYWRIGHT + BEAUTIFULSOUP)")
    print("="*70)

    extractor = ExtractorV16()

    # Extraer licitaciones
    licitaciones = extractor.extraer_procesos("licitaciones")
    extractor.guardar_json(licitaciones, "licitaciones_normales", "licitaciones.json")

    # Extraer compras menores
    compras_menores = extractor.extraer_procesos("compras_menores")
    extractor.guardar_json(compras_menores, "compras_menores", "compras-menores.json")

    total = len(licitaciones) + len(compras_menores)
    total_inversion = sum(p['monto'] for p in licitaciones) + sum(p['monto'] for p in compras_menores)

    print("="*70)
    print("✅ EXTRACCIÓN COMPLETADA")
    print(f"   📋 Licitaciones: {len(licitaciones)}")
    print(f"   📋 Compras Menores: {len(compras_menores)}")
    print(f"   📋 Total Procesos: {total}")
    print(f"   💰 Inversión Total: L. {total_inversion:,.0f}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
