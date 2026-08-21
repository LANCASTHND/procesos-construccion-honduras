#!/usr/bin/env python3
"""Importador de procesos desde CSV - Para datos reales de SICC"""

import csv
import json
import sys
from datetime import datetime

def importar_csv(archivo_csv, tipo_licitacion="licitacion_normal"):
    """
    Importa procesos desde CSV
    Columnas esperadas: expediente, descripcion, institucion, monto, cierre, contacto, link, tipo_licitacion
    """
    print(f"📥 Importando desde {archivo_csv}...")

    procesos = []
    contactos = {
        "UNAH": "unah-compras@unah.edu.hn",
        "UNA": "compras@una.hn",
        "UNACIFOR": "compras@unacifor.hn",
        "SIT": "licitaciones@sit.gob.hn",
        "SEDENA": "compras@sedena.mil.hn",
        "SESEGU": "compras@sesegu.gob.hn",
        "IHT": "compras@iht.hn",
        "TEGUCIGALPA": "compras@tegucigalpa.gob.hn",
        "SESALUD": "compras@sesalud.gob.hn",
    }

    try:
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for idx, row in enumerate(reader, 1):
                try:
                    expediente = row.get('expediente', '').strip()
                    descripcion = row.get('descripcion', '').strip()
                    institucion = row.get('institucion', 'DESCONOCIDA').strip().upper()
                    monto = float(row.get('monto', '0').replace(',', ''))
                    cierre = row.get('cierre', '').strip()  # DD/MM/YYYY
                    contacto = row.get('contacto', contactos.get(institucion, 'contacto@honduras.gob.hn')).strip()
                    link = row.get('link', '').strip()
                    tipo = row.get('tipo_licitacion', tipo_licitacion).strip()

                    # Calcular días para cierre
                    try:
                        fecha_cierre = datetime.strptime(cierre, '%d/%m/%Y')
                        hoy = datetime.now()
                        dias = (fecha_cierre - hoy).days
                    except:
                        dias = 0
                        print(f"   ⚠️  Fila {idx}: No se pudo parsear fecha {cierre}")
                        continue

                    # Skip si ya está cerrado
                    if dias < 0:
                        print(f"   ⚠️  Fila {idx}: {expediente} ya está cerrado ({dias} días)")
                        continue

                    proceso = {
                        "nro": len(procesos) + 1,
                        "expediente": expediente,
                        "descripcion": descripcion,
                        "institucion": institucion,
                        "monto": int(monto),
                        "cierre": cierre,
                        "contacto": contacto,
                        "link": link,
                        "dias_para_cierre": dias,
                        "tipo_licitacion": tipo,
                        "estado_proceso": "vigente" if dias > 0 else "cerrada",
                        "fecha_extraccion": datetime.now().strftime("%Y-%m-%d")
                    }

                    procesos.append(proceso)
                    print(f"   ✓ {expediente} ({dias} días)")

                except Exception as e:
                    print(f"   ✗ Fila {idx}: Error - {e}")
                    continue

        return procesos

    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {archivo_csv}")
        return []
    except Exception as e:
        print(f"❌ Error importando: {e}")
        return []

def guardar_json(procesos, archivo_salida):
    """Guarda procesos en JSON"""
    total = len(procesos)
    inversion = sum(p.get('monto', 0) for p in procesos)

    datos = {
        "metadata": {
            "tipo": "licitaciones_normales",
            "total_procesos": total,
            "inversion_total": inversion,
            "moneda": "Lempiras (L.)",
            "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d"),
            "estado": "vigentes",
            "cobertura": "Honduras",
            "fuente": "Importación Manual desde SICC"
        },
        "procesos": procesos
    }

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Guardado: {archivo_salida}")
    print(f"   📊 Total: {total} procesos")
    print(f"   💰 Inversión: L. {inversion:,.0f}")

if __name__ == "__main__":
    # Importar licitaciones
    print("="*60)
    print("📥 IMPORTADOR DE DATOS REALES DESDE SICC")
    print("="*60 + "\n")

    # Verificar archivo de entrada
    csv_licitaciones = "data/PLANTILLA_IMPORTAR.csv"

    print("🔍 Licitaciones:\n")
    procesos_lic = importar_csv(csv_licitaciones, "licitacion_normal")

    if procesos_lic:
        guardar_json(procesos_lic, "data/licitaciones.json")

    print("\n" + "="*60)
    print("💡 Cómo usar:")
    print("="*60)
    print("""
1. Copiar datos de SICC Honduras Compras
2. Pegar en: data/PLANTILLA_IMPORTAR.csv
3. Ejecutar: python3 scripts/importar_desde_csv.py
4. Generar reportes: python3 scripts/generar_reportes.py
""")
