#!/usr/bin/env python3
"""
Monitor UNGM - Detecta procesos nuevos
Compara datos actuales con histórico y alerta sobre cambios
"""

import json
import os
import hashlib
from datetime import datetime

class MonitorUNGM:
    """Monitorea cambios en procesos UNGM"""

    def __init__(self):
        self.archivo_datos = 'data/ungm-honduras.json'
        self.archivo_historico = 'data/.ungm-historico.json'
        self.archivo_log = 'logs/ungm-monitor.log'
        os.makedirs('logs', exist_ok=True)

    def cargar_datos_actuales(self):
        """Carga datos actuales"""
        if os.path.exists(self.archivo_datos):
            with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"procesos": []}

    def cargar_historico(self):
        """Carga datos históricos previos"""
        if os.path.exists(self.archivo_historico):
            with open(self.archivo_historico, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"procesos": []}

    def guardar_historico(self, datos):
        """Guarda histórico para próxima comparación"""
        with open(self.archivo_historico, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    def generar_hash_proceso(self, proceso):
        """Genera hash único para un proceso"""
        texto = f"{proceso.get('referencia', '')}{proceso.get('titulo', '')}{proceso.get('pais', '')}"
        return hashlib.md5(texto.encode()).hexdigest()

    def detectar_cambios(self, actuales, historicos):
        """Detecta procesos nuevos, modificados y removidos"""
        hash_historico = {self.generar_hash_proceso(p): p for p in historicos.get('procesos', [])}
        hash_actual = {self.generar_hash_proceso(p): p for p in actuales.get('procesos', [])}

        nuevos = []
        modificados = []
        removidos = []

        # Procesos nuevos
        for hash_id, proceso in hash_actual.items():
            if hash_id not in hash_historico:
                nuevos.append(proceso)

        # Procesos modificados
        for hash_id, proceso in hash_actual.items():
            if hash_id in hash_historico:
                historico = hash_historico[hash_id]
                if proceso.get('fecha_cierre') != historico.get('fecha_cierre') or \
                   proceso.get('titulo') != historico.get('titulo'):
                    modificados.append({
                        'proceso': proceso,
                        'cambios': {
                            'fecha_cierre_anterior': historico.get('fecha_cierre'),
                            'fecha_cierre_actual': proceso.get('fecha_cierre')
                        }
                    })

        # Procesos removidos
        for hash_id, proceso in hash_historico.items():
            if hash_id not in hash_actual:
                removidos.append(proceso)

        return nuevos, modificados, removidos

    def generar_reporte(self, nuevos, modificados, removidos):
        """Genera reporte de cambios"""
        reporte = []
        reporte.append(f"{'=' * 70}")
        reporte.append(f"📊 UNGM Monitor - Reporte de Cambios")
        reporte.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        reporte.append(f"{'=' * 70}\n")

        # Nuevos procesos
        if nuevos:
            reporte.append(f"🆕 PROCESOS NUEVOS ({len(nuevos)})")
            reporte.append("-" * 70)
            for proc in nuevos:
                reporte.append(f"  ✅ {proc.get('referencia', 'N/A')}")
                reporte.append(f"     Título: {proc.get('titulo', 'N/A')[:60]}")
                reporte.append(f"     Cierre: {proc.get('fecha_cierre', 'N/A')}")
                reporte.append(f"     URL: {proc.get('url', 'N/A')[:50]}")
                reporte.append("")
        else:
            reporte.append("🆕 PROCESOS NUEVOS: Ninguno")
            reporte.append("")

        # Procesos modificados
        if modificados:
            reporte.append(f"✏️  PROCESOS MODIFICADOS ({len(modificados)})")
            reporte.append("-" * 70)
            for item in modificados:
                proc = item['proceso']
                cambios = item['cambios']
                reporte.append(f"  🔄 {proc.get('referencia', 'N/A')}")
                reporte.append(f"     Título: {proc.get('titulo', 'N/A')[:60]}")
                if cambios.get('fecha_cierre_anterior') != cambios.get('fecha_cierre_actual'):
                    reporte.append(f"     Cierre anterior: {cambios.get('fecha_cierre_anterior')}")
                    reporte.append(f"     Cierre actual: {cambios.get('fecha_cierre_actual')}")
                reporte.append("")
        else:
            reporte.append("✏️  PROCESOS MODIFICADOS: Ninguno")
            reporte.append("")

        # Procesos removidos
        if removidos:
            reporte.append(f"🗑️  PROCESOS REMOVIDOS ({len(removidos)})")
            reporte.append("-" * 70)
            for proc in removidos:
                reporte.append(f"  ❌ {proc.get('referencia', 'N/A')}")
                reporte.append(f"     Título: {proc.get('titulo', 'N/A')[:60]}")
                reporte.append("")
        else:
            reporte.append("🗑️  PROCESOS REMOVIDOS: Ninguno")
            reporte.append("")

        # Resumen
        reporte.append(f"{'=' * 70}")
        reporte.append(f"📋 RESUMEN")
        reporte.append(f"  Total Nuevos: {len(nuevos)}")
        reporte.append(f"  Total Modificados: {len(modificados)}")
        reporte.append(f"  Total Removidos: {len(removidos)}")
        reporte.append(f"{'=' * 70}\n")

        return "\n".join(reporte)

    def guardar_log(self, contenido):
        """Guarda reporte en log"""
        with open(self.archivo_log, 'a', encoding='utf-8') as f:
            f.write(contenido)
            f.write("\n" + "=" * 70 + "\n\n")

    def ejecutar_monitoreo(self):
        """Ejecuta monitoreo completo"""
        print("🔍 Iniciando monitoreo UNGM...")
        print("")

        actuales = self.cargar_datos_actuales()
        historicos = self.cargar_historico()

        if not historicos.get('procesos'):
            print("⚠️  Primera ejecución - Guardando como referencia")
            self.guardar_historico(actuales)
            print(f"📊 Procesos guardados: {len(actuales.get('procesos', []))}")
            return True

        nuevos, modificados, removidos = self.detectar_cambios(actuales, historicos)
        reporte = self.generar_reporte(nuevos, modificados, removidos)

        print(reporte)
        self.guardar_log(reporte)

        # Actualizar histórico
        self.guardar_historico(actuales)

        # Retornar resultado
        hay_cambios = len(nuevos) > 0 or len(modificados) > 0 or len(removidos) > 0
        return hay_cambios


def main():
    """Función principal"""
    monitor = MonitorUNGM()
    hay_cambios = monitor.ejecutar_monitoreo()

    if hay_cambios:
        print("\n🚨 IMPORTANTE: Se detectaron cambios en procesos UNGM")
        print("📋 Ver reporte completo: logs/ungm-monitor.log")
        print("📊 Generar reporte HTML: python3 scripts/generar_reporte_ungm.py")
    else:
        print("\n✅ Sin cambios detectados en procesos UNGM")

if __name__ == '__main__':
    main()
