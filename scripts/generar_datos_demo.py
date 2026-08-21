#!/usr/bin/env python3
"""
Generador de datos de demostración realistas
Crea datos similares a los que Honduras Compras estaría devolviendo
"""

import json
from datetime import datetime, timedelta
import random

class GeneradorDatosDemo:
    """Genera datos realistas para demostración"""

    def __init__(self):
        self.fecha_hoy = datetime(2026, 8, 21)

        self.instituciones_licitaciones = [
            {"sigla": "UNAH", "nombre": "Universidad Nacional Autónoma de Honduras", "email": "unah-compras@unah.edu.hn"},
            {"sigla": "SIT", "nombre": "Servicio de Implementación Técnica", "email": "licitaciones@sit.gob.hn"},
            {"sigla": "UNA", "nombre": "Universidad Nacional Agrícola", "email": "compras@una.hn"},
            {"sigla": "SEDENA", "nombre": "Secretaría de Defensa Nacional", "email": "compras@sedena.mil.hn"},
            {"sigla": "IHT", "nombre": "Instituto Hondureño de Turismo", "email": "compras@iht.hn"},
            {"sigla": "SESEGU", "nombre": "Secretaría de Seguridad", "email": "compras@sesegu.gob.hn"},
            {"sigla": "TEGUCIGALPA", "nombre": "Municipalidad de Tegucigalpa", "email": "compras@tegucigalpa.gob.hn"},
            {"sigla": "SAN PEDRO SULA", "nombre": "Municipalidad de San Pedro Sula", "email": "compras@sanpedrosula.gob.hn"},
        ]

        self.tipos_proyectos = [
            "Construcción de aulas escolares",
            "Remodelación de edificio administrativo",
            "Ampliación de infraestructura sanitaria",
            "Reparación de techos en institución educativa",
            "Pavimentación de acceso principal",
            "Sistema de drenaje pluvial",
            "Construcción de biblioteca municipal",
            "Remodelación de sanitarios",
            "Construcción de cancha deportiva",
            "Pintura y mantenimiento de estructura",
        ]

        self.departamentos = [
            "Francisco Morazán", "Cortés", "La Paz", "Atlántida",
            "El Paraíso", "Comayagua", "Gracias a Dios", "Olancho"
        ]

    def generar_licitaciones(self, cantidad=15):
        """Genera licitaciones realistas"""
        procesos = []

        montos_licitacion = [
            2500000, 3800000, 4200000, 5600000, 6200000,
            7500000, 8900000, 10200000, 12500000, 15000000
        ]

        for i in range(1, cantidad + 1):
            inst = random.choice(self.instituciones_licitaciones)
            dias_hasta_cierre = random.randint(3, 45)
            cierre = self.fecha_hoy + timedelta(days=dias_hasta_cierre)

            proceso = {
                "nro": i,
                "expediente": f"LPN-{inst['sigla']}-{random.randint(1000, 9999)}-2026",
                "descripcion": random.choice(self.tipos_proyectos),
                "institucion": inst['sigla'],
                "monto": random.choice(montos_licitacion),
                "cierre": cierre.strftime("%Y-%m-%d"),
                "contacto": inst['email'],
                "link": f"http://sicc.honducompras.gob.hn/HC/procesos/detalles/{random.randint(10000, 99999)}",
                "dias_para_cierre": dias_hasta_cierre,
                "tipo_licitacion": "licitacion_normal",
                "estado_proceso": "vigente" if dias_hasta_cierre > 0 else "cerrada",
                "fecha_extraccion": self.fecha_hoy.strftime("%Y-%m-%d"),
                "departamento": random.choice(self.departamentos),
                "tipo_proyecto": "construccion" if "construcción" in random.choice(self.tipos_proyectos).lower() else "remodelacion"
            }
            procesos.append(proceso)

        return procesos

    def generar_compras_menores(self, cantidad=20):
        """Genera compras menores realistas"""
        procesos = []

        montos_compra = [
            75000, 95000, 120000, 145000, 165000,
            185000, 205000, 225000, 240000, 250000
        ]

        for i in range(1, cantidad + 1):
            inst = random.choice(self.instituciones_licitaciones)
            dias_hasta_cierre = random.randint(2, 30)
            cierre = self.fecha_hoy + timedelta(days=dias_hasta_cierre)

            proceso = {
                "nro": i,
                "expediente": f"CM-{inst['sigla']}-{random.randint(1000, 9999)}-2026",
                "descripcion": random.choice(self.tipos_proyectos),
                "institucion": inst['sigla'],
                "monto": random.choice(montos_compra),
                "cierre": cierre.strftime("%Y-%m-%d"),
                "contacto": inst['email'],
                "link": f"http://sicc.honducompras.gob.hn/HC/procesos/detalles/{random.randint(10000, 99999)}",
                "dias_para_cierre": dias_hasta_cierre,
                "tipo_licitacion": "compra_menor",
                "estado_proceso": "vigente" if dias_hasta_cierre > 0 else "cerrada",
                "fecha_extraccion": self.fecha_hoy.strftime("%Y-%m-%d"),
                "departamento": random.choice(self.departamentos),
                "tipo_proyecto": "reparacion"
            }
            procesos.append(proceso)

        return procesos

    def guardar_datos_demo(self):
        """Guarda datos de demostración en JSON"""

        print("🎨 Generando datos de demostración realistas...\n")

        # Generar licitaciones
        licitaciones = self.generar_licitaciones(18)
        inversion_lic = sum(p['monto'] for p in licitaciones)

        datos_lic = {
            "metadata": {
                "tipo": "licitaciones_normales",
                "total_procesos": len(licitaciones),
                "inversion_total": inversion_lic,
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": self.fecha_hoy.strftime("%Y-%m-%d"),
                "estado": "vigentes",
                "cobertura": "Honduras",
                "fuente": "SICC Honduras Compras"
            },
            "procesos": licitaciones
        }

        # Generar compras menores
        compras = self.generar_compras_menores(25)
        inversion_comp = sum(p['monto'] for p in compras)

        datos_comp = {
            "metadata": {
                "tipo": "compras_menores",
                "total_procesos": len(compras),
                "inversion_total": inversion_comp,
                "moneda": "Lempiras (L.)",
                "fecha_actualizacion": self.fecha_hoy.strftime("%Y-%m-%d"),
                "estado": "vigentes",
                "cobertura": "Honduras",
                "rango_monto": "75000-250000",
                "fuente": "SICC Honduras Compras"
            },
            "procesos": compras
        }

        # Guardar archivos
        with open('data/licitaciones.json', 'w', encoding='utf-8') as f:
            json.dump(datos_lic, f, ensure_ascii=False, indent=2)

        with open('data/compras-menores.json', 'w', encoding='utf-8') as f:
            json.dump(datos_comp, f, ensure_ascii=False, indent=2)

        print(f"✅ Licitaciones normales: {len(licitaciones)} procesos")
        print(f"   💰 Inversión total: L. {inversion_lic:,.0f}\n")

        print(f"✅ Compras menores: {len(compras)} procesos")
        print(f"   💰 Inversión total: L. {inversion_comp:,.0f}\n")

        print(f"✅ Total general: {len(licitaciones) + len(compras)} procesos")
        print(f"   💰 Inversión global: L. {inversion_lic + inversion_comp:,.0f}\n")

if __name__ == "__main__":
    generador = GeneradorDatosDemo()
    generador.guardar_datos_demo()
    print("✅ Datos de demostración generados exitosamente")
