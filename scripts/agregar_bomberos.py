#!/usr/bin/env python3
"""
Agregar manualmente proceso de Cuerpo de Bomberos encontrado en SICC
"""

import json
from datetime import datetime, timedelta

# Datos del proceso
proceso = {
    "expediente": "GC-LPN-HBCBH-INFRAESTRUCTURA-004-2026",
    "descripcion": "Proceso Licitacion",
    "institucion": "CUERPO DE BOMBEROS",
    "modalidad": "Licitación pública nacional",
    "etapa": "Recepción de Ofertas",
    "cierre": "25/09/2026",
    "monto": 0,
    "dias_para_cierre": (datetime.strptime("25/09/2026", "%d/%m/%Y") - datetime.now()).days,
    "tipo_licitacion": "licitacion",
    "link": "#",
    "contacto": "compras@cuerpodbomberos.hn",
    "estado_proceso": "vigente",
    "fecha_extraccion": datetime.now().strftime("%Y-%m-%d"),
    "objeto": "INCREMENTAR LA CAPACIDAD INSTALADA DE INFRAESTRUCTURA BOMBERIL, ADECUADA, SEGURA, FUNCIONAL Y TERRITORIALMENTE DISTRIBUIDA PARA BRINDAR SERVICIOS OPORTUNOS",
    "fecha_inicio": "24/08/2026"
}

# Cargar licitaciones
with open('data/licitaciones.json', 'r', encoding='utf-8') as f:
    datos = json.load(f)

# Verificar si ya existe
expediente_existe = any(p['expediente'].strip() == proceso['expediente'].strip()
                        for p in datos['procesos'])

if expediente_existe:
    print("✓ Proceso ya existe en datos")
else:
    # Agregar
    datos['procesos'].append(proceso)
    datos['procesos'].sort(key=lambda x: x.get('cierre', ''), reverse=True)
    datos['metadata']['total_procesos'] = len(datos['procesos'])
    datos['metadata']['fecha_actualizacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar
    with open('data/licitaciones.json', 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

    print(f"✓ Proceso agregado: {proceso['expediente']}")
    print(f"✓ Total licitaciones: {len(datos['procesos'])}")
