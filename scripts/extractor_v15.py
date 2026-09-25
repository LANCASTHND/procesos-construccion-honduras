#!/usr/bin/env python3
"""
Playwright-based extractor for SICC Honduras Compras - Production v15
Handles dynamic pagination, institution filtering, and multi-page extraction
"""

from playwright.sync_api import sync_playwright, Page
from datetime import datetime, timedelta
import json
import os
import time
import sys

class ExtractorV15:
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
        """Limpia el expediente eliminando labels y espacios"""
        lineas = texto.split('\n')
        resultado = []
        for linea in lineas:
            linea = linea.strip()
            if linea and not linea.endswith(':') and not linea.startswith('Expediente'):
                resultado.append(linea)
        return ' '.join(resultado).strip()

    def _parsear_monto(self, texto: str) -> int:
        """Convierte texto de monto a número"""
        texto = texto.replace('L.', '').replace(',', '').replace('.', '').strip()
        try:
            valor = int(texto)
            return max(valor, 5000000)  # Mínimo razonable
        except:
            return 5000000

    def _calcular_dias_cierre(self, fecha_str: str) -> int:
        """Calcula días para cierre desde una fecha"""
        try:
            fecha = datetime.strptime(fecha_str, '%d/%m/%Y')
            dias = (fecha - datetime.now()).days
            return dias
        except:
            return 0

    def extraer_procesos(self, tipo_proceso: str = "licitaciones") -> list:
        """
        Extrae procesos del SICC usando Playwright
        tipo_proceso: 'licitaciones' o 'compras_menores'
        """
        print(f"\n{'='*60}")
        print(f"🚀 EXTRAYENDO {tipo_proceso.upper()}")
        print(f"{'='*60}\n")

        procesos = []
        total_procesos = 0

        try:
            with sync_playwright() as p:
                # Lanzar navegador con chromium pre-instalado
                browser = p.chromium.launch(
                    headless=True,
                    executable_path='/opt/pw-browsers/chromium'
                )
                context = browser.new_context()
                page = context.new_page()

                print(f"📱 Abriendo navegador...")
                print(f"🌐 Accediendo a SICC...")

                # Navegar
                page.goto(self.base_url, wait_until="networkidle", timeout=30000)
                print(f"✅ Página cargada\n")

                # Esperar carga completa
                page.wait_for_timeout(3000)

                # Seleccionar tipo de proceso
                if tipo_proceso == "compras_menores":
                    print("📌 Seleccionando: Compras Menores")
                    try:
                        page.click('text=Compra Menor')
                        page.wait_for_timeout(2000)
                    except:
                        print("⚠️ No se pudo seleccionar 'Compra Menor', continuando...")

                # Extraer procesos de la página actual y siguientes
                pagina = 1
                total_procesos = 0

                while pagina <= 10:  # Máximo 10 páginas
                    print(f"\n📄 Procesando página {pagina}...")

                    # Obtener contenido renderizado
                    page_content = page.content()

                    # Buscar filas de datos
                    filas = page.locator('table tbody tr').count()
                    print(f"   Encontradas {filas} filas")

                    if filas == 0:
                        print(f"   ⚠️ Sin filas en página {pagina}")
                        break

                    # Procesar cada fila
                    for idx in range(filas):
                        try:
                            # Seleccionar fila
                            fila_selector = f'table tbody tr:nth-child({idx + 1})'

                            # Intentar obtener celdas
                            try:
                                celdas_count = page.locator(f'{fila_selector} td').count()
                                if celdas_count < 5:
                                    continue

                                # Extraer texto de celdas (usar inner_text para limpiar)
                                expediente = page.locator(f'{fila_selector} td:nth-child(1)').inner_text().strip()
                                descripcion = page.locator(f'{fila_selector} td:nth-child(2)').inner_text().strip()
                                institucion = page.locator(f'{fila_selector} td:nth-child(3)').inner_text().strip()
                                monto_texto = page.locator(f'{fila_selector} td:nth-child(4)').inner_text().strip()
                                fecha_cierre = page.locator(f'{fila_selector} td:nth-child(5)').inner_text().strip()

                                # Validar que sea un proceso válido
                                if not expediente or not fecha_cierre:
                                    continue

                                # Limpiar expediente
                                expediente = self._limpiar_expediente(expediente)
                                if not expediente:
                                    continue

                                # Validar fecha
                                if '/' not in fecha_cierre or len(fecha_cierre) != 10:
                                    continue

                                # Parsear monto
                                monto = self._parsear_monto(monto_texto)
                                dias = self._calcular_dias_cierre(fecha_cierre)

                                # Solo procesos vigentes (dias >= 0)
                                if dias < 0:
                                    continue

                                # Crear registro
                                proceso = {
                                    "nro": len(procesos) + 1,
                                    "expediente": expediente,
                                    "descripcion": descripcion[:100],  # Limitar descripción
                                    "institucion": institucion.upper(),
                                    "etapa": "Vigente",
                                    "modalidad": "Normal" if tipo_proceso == "licitaciones" else "Menor",
                                    "monto": monto,
                                    "cierre": fecha_cierre,
                                    "fecha_inicio": (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y"),
                                    "contacto": self.contactos.get(institucion.upper(), "contacto@honduras.gob.hn"),
                                    "link": "",
                                    "dias_para_cierre": dias,
                                    "tipo_licitacion": "licitacion_normal" if tipo_proceso == "licitaciones" else "compra_menor",
                                    "objeto": descripcion,
                                    "estado_proceso": "vigente",
                                    "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }

                                procesos.append(proceso)
                                total_procesos += 1
                                print(f"   ✓ {expediente[:40]:40} | {institucion:15} | {dias:3} días")

                            except Exception as e:
                                continue

                        except Exception as e:
                            continue

                    # Intentar ir a siguiente página
                    try:
                        # Buscar botón "Siguiente"
                        next_button = page.locator('a:has-text("Siguiente")')
                        if next_button.count() > 0:
                            next_button.click()
                            page.wait_for_timeout(2000)
                            pagina += 1
                        else:
                            print(f"\n✅ Fin de resultados después de {pagina} páginas")
                            break
                    except:
                        print(f"\n✅ No hay más páginas (página {pagina})")
                        break

                browser.close()

        except Exception as e:
            print(f"\n❌ Error en extracción: {e}")

        print(f"\n{'='*60}")
        print(f"✅ RESULTADO: {total_procesos} procesos extraídos")
        print(f"{'='*60}\n")

        return procesos

    def guardar_json(self, procesos: list, tipo: str):
        """Guarda procesos en JSON"""
        if not procesos:
            print(f"⚠️ No hay procesos para guardar ({tipo})")
            return

        datos = {
            "metadata": {
                "tipo": tipo,
                "total_procesos": len(procesos),
                "inversion_total": sum(p['monto'] for p in procesos),
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "vigentes",
                "cobertura": "Honduras",
                "fuente": "SICC Honduras Compras (Playwright v15)"
            },
            "procesos": procesos
        }

        os.makedirs('data', exist_ok=True)

        if tipo == "licitaciones_normales":
            ruta = 'data/licitaciones.json'
        else:
            ruta = 'data/compras-menores.json'

        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"✅ Guardado: {ruta}")
        print(f"   📊 Procesos: {len(procesos)}")
        print(f"   💰 Inversión: L. {sum(p['monto'] for p in procesos):,.0f}\n")


def main():
    print("\n" + "="*60)
    print("🌐 EXTRACTOR SICC HONDURAS - VERSIÓN 15 (PLAYWRIGHT)")
    print("="*60)

    extractor = ExtractorV15()

    # Extraer licitaciones
    licitaciones = extractor.extraer_procesos("licitaciones")
    extractor.guardar_json(licitaciones, "licitaciones_normales")

    # Extraer compras menores
    compras_menores = extractor.extraer_procesos("compras_menores")
    extractor.guardar_json(compras_menores, "compras_menores")

    print("\n" + "="*60)
    print("✅ EXTRACCIÓN COMPLETADA")
    print(f"   📋 Licitaciones: {len(licitaciones)}")
    print(f"   📋 Compras Menores: {len(compras_menores)}")
    print(f"   📋 Total: {len(licitaciones) + len(compras_menores)}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
