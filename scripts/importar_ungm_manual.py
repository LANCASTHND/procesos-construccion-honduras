#!/usr/bin/env python3
"""
Importador Manual de Procesos UNGM
Permite copiar procesos desde UNGM y formatearlos automáticamente
"""

import json
import sys
from datetime import datetime

def crear_proceso_desde_fila(referencia, titulo, pais, tipo, fecha_pub, fecha_cierre, url=""):
    """Crea un objeto proceso formateado"""
    return {
        "referencia": referencia.strip(),
        "titulo": titulo.strip(),
        "pais": pais.strip(),
        "tipo": tipo.strip(),
        "fecha_publicado": fecha_pub.strip(),
        "fecha_cierre": fecha_cierre.strip(),
        "url": url.strip()
    }

def importar_desde_csv(archivo_csv):
    """Importa procesos desde un archivo CSV"""
    procesos = []
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            lineas = f.readlines()[1:]  # Saltar header
            for linea in lineas:
                partes = linea.strip().split('\t')  # Asumir separado por tabulación
                if len(partes) >= 6:
                    proceso = crear_proceso_desde_fila(*partes[:7])
                    procesos.append(proceso)
        return procesos
    except Exception as e:
        print(f"Error importando CSV: {e}")
        return []

def importar_interactivo():
    """Modo interactivo para agregar procesos"""
    procesos = []
    print("\n📝 Modo Interactivo - Ingresa procesos de UNGM")
    print("=" * 60)
    print("Escribe 'fin' en Referencia para terminar\n")

    while True:
        print(f"\n📌 Proceso #{len(procesos) + 1}")
        referencia = input("Referencia: ").strip()

        if referencia.lower() == 'fin':
            break

        titulo = input("Título: ").strip()
        pais = input("País: ").strip()
        tipo = input("Tipo (Materials/Construction/Services): ").strip()
        fecha_pub = input("Fecha Publicado (YYYY-MM-DD): ").strip()
        fecha_cierre = input("Fecha Cierre (YYYY-MM-DD): ").strip()
        url = input("URL UNGM (opcional): ").strip()

        if referencia and titulo and pais:
            proceso = crear_proceso_desde_fila(
                referencia, titulo, pais, tipo, fecha_pub, fecha_cierre, url
            )
            procesos.append(proceso)
            print(f"✅ Proceso agregado ({len(procesos)} total)")
        else:
            print("⚠️  Referencia, Título y País son requeridos")

    return procesos

def generar_json(procesos, archivo_salida="data/ungm-honduras.json"):
    """Genera archivo JSON con procesos"""
    datos = {
        "metadata": {
            "fuente": "UNGM - United Nations Global Marketplace",
            "url": "https://www.ungm.org/Public/Notice",
            "tipo": "Procesos de Construcción y Materiales - Honduras",
            "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d"),
            "total_procesos": len(procesos),
            "moneda": "USD",
            "cobertura": "Honduras - Procesos de Construcción y Materiales",
            "filtros_aplicados": "País: Honduras, Tipos: Construcción/Materiales",
            "metodo_extraccion": "Importación manual desde UNGM"
        },
        "procesos": procesos
    }

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Guardado: {archivo_salida}")
    print(f"   Total procesos: {len(procesos)}")
    return True

def mostrar_instrucciones():
    """Muestra cómo usar la herramienta"""
    print("""
🌍 Importador Manual UNGM
========================

OPCIÓN 1: Modo Interactivo
python3 scripts/importar_ungm_manual.py

OPCIÓN 2: Desde CSV
python3 scripts/importar_ungm_manual.py archivo.csv

Formato CSV esperado (tabulación separada):
Referencia	Título	País	Tipo	Fecha Publicado	Fecha Cierre	URL

Ejemplo:
UNGM-2026-001	Supply of Materials	Honduras	Materials	2026-08-20	2026-09-15	https://...
UNGM-2026-002	Construction Services	Honduras	Construction	2026-08-18	2026-09-18	https://...
""")

def main():
    """Función principal"""
    print("🌍 Importador de Procesos UNGM")
    print("=" * 60)

    if len(sys.argv) > 1:
        archivo = sys.argv[1]
        if archivo.endswith('.csv') or archivo.endswith('.txt'):
            print(f"📂 Importando desde: {archivo}")
            procesos = importar_desde_csv(archivo)
            if procesos:
                generar_json(procesos)
                print("✅ Importación completada")
            else:
                print("⚠️  No se encontraron procesos")
        else:
            mostrar_instrucciones()
    else:
        procesos = importar_interactivo()
        if procesos:
            generar_json(procesos)
            print("✅ Procesos importados y guardados")
        else:
            print("⚠️  No se agregaron procesos")

if __name__ == '__main__':
    main()
