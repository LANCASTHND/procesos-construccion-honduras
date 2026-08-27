#!/usr/bin/env python3
"""
Sistema de monitoreo de salud para Honduras Procurement System
Verifica estado de extracción, generación de reportes y sincronización
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class HealthMonitor:
    """Monitorea la salud del sistema de procesos Honduras"""

    def __init__(self):
        self.data_dir = "data"
        self.reports_dir = "reportes"
        self.thresholds = {
            "data_age_hours": 24,
            "extraction_time_seconds": 60,
            "report_size_kb": 1,
            "min_processes": 0,  # Allow 0 for template data
        }

    def verificar_archivos_datos(self):
        """Verifica que los archivos de datos existan y sean válidos"""
        checks = {}

        # Verificar licitaciones.json
        lic_path = Path(self.data_dir) / "licitaciones.json"
        if lic_path.exists():
            try:
                with open(lic_path, 'r', encoding='utf-8') as f:
                    lic_data = json.load(f)
                checks['licitaciones_json'] = {
                    'status': '✅ OK',
                    'size_kb': lic_path.stat().st_size / 1024,
                    'procesos': lic_data.get('metadata', {}).get('total_procesos', 0),
                    'inversion': f"L. {lic_data.get('metadata', {}).get('inversion_total', 0):,.0f}"
                }
            except Exception as e:
                checks['licitaciones_json'] = {'status': f'❌ Error: {str(e)}'}
        else:
            checks['licitaciones_json'] = {'status': '❌ Archivo no encontrado'}

        # Verificar compras-menores.json
        cm_path = Path(self.data_dir) / "compras-menores.json"
        if cm_path.exists():
            try:
                with open(cm_path, 'r', encoding='utf-8') as f:
                    cm_data = json.load(f)
                checks['compras_menores_json'] = {
                    'status': '✅ OK',
                    'size_kb': cm_path.stat().st_size / 1024,
                    'procesos': cm_data.get('metadata', {}).get('total_procesos', 0),
                    'inversion': f"L. {cm_data.get('metadata', {}).get('inversion_total', 0):,.0f}"
                }
            except Exception as e:
                checks['compras_menores_json'] = {'status': f'❌ Error: {str(e)}'}
        else:
            checks['compras_menores_json'] = {'status': '❌ Archivo no encontrado'}

        return checks

    def verificar_reportes_html(self):
        """Verifica que los reportes HTML existan y sean válidos"""
        checks = {}

        reports = ['licitaciones.html', 'compras-menores.html']
        for report_name in reports:
            report_path = Path(self.reports_dir) / report_name
            if report_path.exists():
                size_kb = report_path.stat().st_size / 1024
                checks[report_name] = {
                    'status': '✅ OK',
                    'size_kb': size_kb,
                    'last_modified': datetime.fromtimestamp(report_path.stat().st_mtime).isoformat()
                }
            else:
                checks[report_name] = {'status': '❌ Archivo no encontrado'}

        return checks

    def verificar_freshness_datos(self):
        """Verifica que los datos sean recientes"""
        freshness = {}

        try:
            with open(Path(self.data_dir) / "licitaciones.json", 'r', encoding='utf-8') as f:
                lic_data = json.load(f)
                fecha_update = lic_data.get('metadata', {}).get('fecha_actualizacion', 'N/A')
                if fecha_update != 'N/A':
                    update_date = datetime.strptime(fecha_update, '%Y-%m-%d')
                    hours_old = (datetime.now() - update_date).total_seconds() / 3600
                    if hours_old <= self.thresholds['data_age_hours']:
                        freshness['data_freshness'] = {
                            'status': '✅ Datos actuales',
                            'last_update': fecha_update,
                            'hours_old': round(hours_old, 1)
                        }
                    else:
                        freshness['data_freshness'] = {
                            'status': '⚠️  Datos antiguos',
                            'last_update': fecha_update,
                            'hours_old': round(hours_old, 1)
                        }
        except Exception as e:
            freshness['data_freshness'] = {'status': f'❌ Error: {str(e)}'}

        return freshness

    def generar_reporte_salud(self):
        """Genera reporte completo de salud del sistema"""
        print("\n" + "="*70)
        print("🏥 HONDURAS PROCUREMENT SYSTEM - HEALTH CHECK")
        print("="*70)
        print(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Verificar datos
        print("📊 DATA FILES STATUS:")
        datos_checks = self.verificar_archivos_datos()
        for file_name, status in datos_checks.items():
            print(f"  {file_name}: {status.get('status', 'N/A')}")
            if 'procesos' in status:
                print(f"    └─ Procesos: {status['procesos']}, Inversión: {status['inversion']}")

        # Verificar reportes
        print("\n📄 REPORT FILES STATUS:")
        reports_checks = self.verificar_reportes_html()
        for report_name, status in reports_checks.items():
            print(f"  {report_name}: {status.get('status', 'N/A')}")
            if 'size_kb' in status:
                print(f"    └─ Size: {status['size_kb']:.1f} KB, Last update: {status.get('last_modified', 'N/A')}")

        # Verificar actualización de datos
        print("\n🔄 DATA FRESHNESS:")
        freshness_checks = self.verificar_freshness_datos()
        for check_name, status in freshness_checks.items():
            print(f"  {status.get('status', 'N/A')}")
            if 'last_update' in status:
                print(f"    └─ Last updated: {status['last_update']} ({status.get('hours_old', 0):.1f} hours ago)")

        # Resumen de métricas
        print("\n📈 PERFORMANCE METRICS:")
        print(f"  Extraction Target: <1 minute")
        print(f"  Report Generation Target: <5 seconds")
        print(f"  Page Load Target: <1 second")
        print(f"  Expected Uptime: 99.9%")

        print("\n" + "="*70)
        print("✅ Health check complete")
        print("="*70 + "\n")

        # Retornar estado general
        all_ok = all(
            'OK' in str(status.get('status', '')) or 'Datos actuales' in str(status.get('status', ''))
            for status in [*datos_checks.values(), *reports_checks.values(), *freshness_checks.values()]
        )
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': '🟢 HEALTHY' if all_ok else '🟡 NEEDS ATTENTION',
            'checks': {
                'data_files': datos_checks,
                'report_files': reports_checks,
                'data_freshness': freshness_checks
            }
        }

def main():
    """Ejecuta el monitoreo de salud"""
    monitor = HealthMonitor()
    health_status = monitor.generar_reporte_salud()

    # Guardar reporte en JSON
    os.makedirs('data', exist_ok=True)
    with open('data/health-status.json', 'w', encoding='utf-8') as f:
        json.dump(health_status, f, ensure_ascii=False, indent=2)

    return health_status

if __name__ == "__main__":
    main()
