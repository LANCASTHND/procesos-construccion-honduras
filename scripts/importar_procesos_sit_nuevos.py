#!/usr/bin/env python3
"""
Importador manual de procesos SIT nuevos detectados en SICC
"""

import json
from datetime import datetime, timedelta

# Procesos nuevos de SIT encontrados en primera página de SICC
nuevos_procesos = [
    {
        "expediente": "CPN-SIT-035-2026",
        "institucion": "SIT",
        "descripcion": "REVISIÓN DEL DISEÑO Y SUPERVISIÓN DE LA CONSTRUCCIÓN MEJORAMIENTO VIAL DE LA INTERSECCIÓN CA-05 – LOARQUE MEDIANTE PASO A DESNIVEL Y RECONFIGURACIÓN...",
        "objeto": "REVISIÓN DEL DISEÑO Y SUPERVISIÓN DE LA CONSTRUCCIÓN MEJORAMIENTO VIAL DE LA INTERSECCIÓN CA-05 – LOARQUE MEDIANTE PASO A DESNIVEL Y RECONFIGURACIÓN FUNCIONAL PARA FLUJO CONTINUO",
        "etapa": "Elaboración",
        "modalidad": "Concurso público nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "31/08/2026",
        "cierre": "17/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPN-SIT-036-2026",
        "institucion": "SIT",
        "descripcion": "CONSTRUCCIÓN MEJORAMIENTO VIAL DE LA INTERSECCIÓN CA-05 – LOARQUE MEDIANTE PASO A DESNIVEL Y RECONFIGURACIÓN FUNCIONAL...",
        "objeto": "CONSTRUCCIÓN MEJORAMIENTO VIAL DE LA INTERSECCIÓN CA-05 – LOARQUE MEDIANTE PASO A DESNIVEL Y RECONFIGURACIÓN FUNCIONAL PARA FLUJO CONTINUO, TEGUCIGALPA",
        "etapa": "Elaboración",
        "modalidad": "Licitación pública nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "31/08/2026",
        "cierre": "17/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "CPI-SIT-BCIE-002-2026",
        "institucion": "SIT",
        "descripcion": "Servicios de Consultoría para el Diseño e Implementación de Planes de Reasentamiento Involuntario (PRI)...",
        "objeto": "Servicios de Consultoría para el Diseño e Implementación de Planes de Reasentamiento Involuntario (PRI), con aplicación de Estándares Internacionales",
        "etapa": "Recepción de Ofertas",
        "modalidad": "Concurso público internacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "13/08/2026",
        "cierre": "14/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "CPN-SIT-030-2026",
        "institucion": "SIT",
        "descripcion": "REDISEÑO Y SUPERVISIÓN DE OBRA PARA LA PAVIMENTACIÓN CON DOBLE TRATAMIENTO SUPERFICIAL, TRAMO No.1...",
        "objeto": "REDISEÑO Y SUPERVISIÓN DE OBRA PARA LA PAVIMENTACIÓN CON DOBLE TRATAMIENTO SUPERFICIAL, TRAMO No.1: RUTA CA-7 - MARCALA - SABANETAS & TRAMO No.2: RUTA CA-7 - MARCALA",
        "etapa": "Elaboración",
        "modalidad": "Concurso público nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "20/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPN-SIT-032-2026",
        "institucion": "SIT",
        "descripcion": "PAVIMENTACIÓN CON DOBLE TRATAMIENTO SUPERFICIAL, TRAMO No.1: RUTA CA-7 - MARCALA - SABANETAS...",
        "objeto": "PAVIMENTACIÓN CON DOBLE TRATAMIENTO SUPERFICIAL, TRAMO No.1: RUTA CA-7 - MARCALA - SABANETAS & TRAMO No.2: RUTA 12V53400, CA-7 - CABAÑAS",
        "etapa": "Elaboración",
        "modalidad": "Licitación pública nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "20/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPN-SIT-033-2026",
        "institucion": "SIT",
        "descripcion": "PAVIMENTACIÓN CON DOBLE TRATAMIENTO SUPERFICIAL, RUTA 165, CA-7 - NAHUATERIQUE...",
        "objeto": "PAVIMENTACIÓN CON DOBLE TRATAMIENTO SUPERFICIAL, RUTA 165, CA-7 - NAHUATERIQUE, APROXIMADAMENTE 10.50 KM, DEPARTAMENTO DE LA PAZ",
        "etapa": "Elaboración",
        "modalidad": "Licitación pública nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "20/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "HN-SIT-531129-CS-INDV",
        "institucion": "SIT",
        "descripcion": "IDENTIFICACIÓN Y REPORTE DE ÁREAS PARA INICIAR PROCESOS DE RESTAURACIÓN...",
        "objeto": "IDENTIFICACIÓN Y REPORTE DE ÁREAS PARA INICIAR PROCESOS DE RESTAURACIÓN",
        "etapa": "Elaboración",
        "modalidad": "Concurso público nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "20/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "HN-SIT-531132-CS-INDV",
        "institucion": "SIT",
        "descripcion": "ELABORACIÓN DE UN DIAGNÓSTICO SOBRE EL USO DE ESPECIES SILVESTRES...",
        "objeto": "ELABORACIÓN DE UN DIAGNÓSTICO SOBRE EL USO DE ESPECIES SILVESTRES PARA CONSUMO O VENTA EN EL ÁREA DE INFLUENCIA DEL PROYECTO CONECTIVIDAD SOSTENIBLE",
        "etapa": "Elaboración",
        "modalidad": "Concurso público nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "20/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "HN-SIT-531135-CS-INDV",
        "institucion": "SIT",
        "descripcion": "IDENTIFICACIÓN DE VIVEROS COMUNITARIOS...",
        "objeto": "IDENTIFICACIÓN DE VIVEROS COMUNITARIOS",
        "etapa": "Elaboración",
        "modalidad": "Concurso público nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "20/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "HN-SIT-564200-CS-INDV",
        "institucion": "SIT",
        "descripcion": "COORINADOR GENERAL DE LA UNIDAD EJECUTORA DEL PROYECTO (UEP)...",
        "objeto": "COORINADOR GENERAL DE LA UNIDAD EJECUTORA DEL PROYECTO (UEP)",
        "etapa": "Elaboración",
        "modalidad": "Concurso público nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "23/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "HN-SIT-564204-CS-INDV",
        "institucion": "SIT",
        "descripcion": "ESPECIALISTA AMBIENTAL DE LA UNIDAD EJECUTORA DEL PROYECTO (UEP)...",
        "objeto": "ESPECIALISTA AMBIENTAL DE LA UNIDAD EJECUTORA DEL PROYECTO (UEP)",
        "etapa": "Elaboración",
        "modalidad": "Concurso público nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "20/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "HN-SIT-564205-CS-INDV",
        "institucion": "SIT",
        "descripcion": "CONSULTORÍA ESPECIALISTA SOCIAL DE LA UNIDAD EJECUTORA DEL PROYECTO (UEP)...",
        "objeto": "CONSULTORÍA ESPECIALISTA SOCIAL DE LA UNIDAD EJECUTORA DEL PROYECTO (UEP)",
        "etapa": "Elaboración",
        "modalidad": "Concurso público nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "24/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "HN-SIT-568279-CS-INDV",
        "institucion": "SIT",
        "descripcion": "ENLACE TECNICO ICF-SIT...",
        "objeto": "ENLACE TECNICO ICF-SIT",
        "etapa": "Elaboración",
        "modalidad": "Concurso público nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "20/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "HN-SIT-568282-CS-INDV",
        "institucion": "SIT",
        "descripcion": "MONITOREO Y SEGUIMIENTO ICF-SIT...",
        "objeto": "MONITOREO Y SEGUIMIENTO ICF-SIT",
        "etapa": "Elaboración",
        "modalidad": "Concurso público nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "20/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "CPN-SIT-031-2026",
        "institucion": "SIT",
        "descripcion": "REDISEÑO Y SUPERVISIÓN DE OBRA PARA LA PAVIMENTACIÓN CON DOBLE TRATAMIENTO SUPERFICIAL...",
        "objeto": "REDISEÑO Y SUPERVISIÓN DE OBRA PARA LA PAVIMENTACIÓN CON DOBLE TRATAMIENTO SUPERFICIAL, RUTA 165, CA-7 - NAHUATERIQUE",
        "etapa": "Elaboración",
        "modalidad": "Concurso público nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "20/08/2026",
        "cierre": "11/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPR-SIT-020-2026",
        "institucion": "SIT",
        "descripcion": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO 4000 PSI, COMUNIDAD BARRIO BUENOS AIRES...",
        "objeto": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO 4000 PSI, COMUNIDAD BARRIO BUENOS AIRES, MUNICIPIO BALFATE, DEPARTAMENTO DE COLÓN",
        "etapa": "Elaboración",
        "modalidad": "Licitación privada",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "28/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPR-SIT-015-2026",
        "institucion": "SIT",
        "descripcion": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO 4000 PSI, BARRIO EL CENTRO...",
        "objeto": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO 4000 PSI, BARRIO EL CENTRO, MUNICIPIO DE LIMÓN, DEPARTAMENTO DE COLÓN",
        "etapa": "Elaboración",
        "modalidad": "Licitación privada",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "28/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPR-SIT-019-2026",
        "institucion": "SIT",
        "descripcion": "PAVIMENTACIÓN DE CONCRETO HIDRÁULICO 4000 PSI, COMUNIDAD DOS BOCAS...",
        "objeto": "PAVIMENTACIÓN DE CONCRETO HIDRÁULICO 4000 PSI, COMUNIDAD DOS BOCAS, MUNICIPIO DE SANTA ROSA DE AGUAN, DEPARTAMENTO DE COLÓN",
        "etapa": "Elaboración",
        "modalidad": "Licitación privada",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "28/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPR-SIT-018-2026",
        "institucion": "SIT",
        "descripcion": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO DE 4000 PSI, BARRIO LAS ACACIAS...",
        "objeto": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO DE 4000 PSI, BARRIO LAS ACACIAS, MUNICIPIO DE BONITO ORIENTAL, DEPARTAMENTO DE COLÓN",
        "etapa": "Elaboración",
        "modalidad": "Licitación privada",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "28/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "SIT-CDE-C0-018-2026",
        "institucion": "SIT",
        "descripcion": "OBRAS DE EMERGENCIA PARA LIMPIEZA Y BACHEO TEMPORAL PALIATIVO...",
        "objeto": "OBRAS DE EMERGENCIA PARA LIMPIEZA Y BACHEO TEMPORAL PALIATIVO",
        "etapa": "Elaboración",
        "modalidad": "Contratación directa",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "31/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPR-SIT-017-2026",
        "institucion": "SIT",
        "descripcion": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO 4000 PSI, COMUNIDAD DE SALAMÁ...",
        "objeto": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO 4000 PSI, COMUNIDAD DE SALAMÁ, MUNICIPIO DE TOCOA, DEPARTAMENTO DE COLÓN",
        "etapa": "Elaboración",
        "modalidad": "Licitación privada",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "28/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPR-SIT-016-2026",
        "institucion": "SIT",
        "descripcion": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO 4000 PSI, COMUNIDAD DE ELIXIR...",
        "objeto": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO 4000 PSI, COMUNIDAD DE ELIXIR, MUNICIPIO DE SABÁ, DEPARTAMENTO DE COLÓN",
        "etapa": "Elaboración",
        "modalidad": "Licitación privada",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "28/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "SIT-CDE-SU-019-2026",
        "institucion": "SIT",
        "descripcion": "SUPERVISIÓN DE LAS OBRAS DE EMERGENCIA PARA LIMPIEZA Y BACHEO TEMPORAL...",
        "objeto": "SUPERVISIÓN DE LAS OBRAS DE EMERGENCIA PARA LIMPIEZA Y BACHEO TEMPORAL PALIATIVO DEL TRAMO: CA13-LA CEIBA - SABÁ",
        "etapa": "Elaboración",
        "modalidad": "Contratación directa",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "31/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "CP-SIT-010-2026",
        "institucion": "SIT",
        "descripcion": "SUPERVISIÓN DE LOS PROYECTOS: 1). PAVIMENTACIÓN CON CONCRETO HIDRÁULICO...",
        "objeto": "SUPERVISIÓN DE LOS PROYECTOS: 1). PAVIMENTACIÓN CON CONCRETO HIDRÁULICO DE 4000 PSI, COMUNIDAD JUAN ANTONIO, MUNICIPIO DE TOCOA",
        "etapa": "Elaboración",
        "modalidad": "Concurso privado",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "28/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPN-SIT-035-2026",
        "institucion": "SIT",
        "descripcion": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO MR= 650...",
        "objeto": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO MR= 650, 13S08210, RUTA 82, CA-11A, TRAMO: LAS FLORES - LEPAERA",
        "etapa": "Elaboración",
        "modalidad": "Licitación pública nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "24/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "CPN-SIT-034-2026",
        "institucion": "SIT",
        "descripcion": "SUPERVISIÓN DE OBRA PARA LA PAVIMENTACIÓN CON CONCRETO HIDRÁULICO MR= 650...",
        "objeto": "SUPERVISIÓN DE OBRA PARA LA PAVIMENTACIÓN CON CONCRETO HIDRÁULICO MR= 650, RUTA 82, CA-11A, TRAMO: LAS FLORES - LEPAERA",
        "etapa": "Elaboración",
        "modalidad": "Licitación pública nacional",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "24/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "CP-SIT-009-2026",
        "institucion": "SIT",
        "descripcion": "SUPERVISIÓN DE LOS PROYECTOS: 1). PAVIMENTACIÓN CON CONCRETO HIDRAULICO...",
        "objeto": "SUPERVISIÓN DE LOS PROYECTOS: 1). PAVIMENTACIÓN CON CONCRETO HIDRAULICO 4000 PSI, COMUNIDAD BARRIO BUENOS AIRES",
        "etapa": "Elaboración",
        "modalidad": "Concurso privado",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "28/08/2026",
        "cierre": "10/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPR-SIT-014-2026",
        "institucion": "SIT",
        "descripcion": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO DE 4000 PSI, COMUNIDAD JUAN ANTONIO...",
        "objeto": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO DE 4000 PSI, COMUNIDAD JUAN ANTONIO, MUNICIPIO DE TOCOA, DEPARTAMENTO DE COLÓN",
        "etapa": "Elaboración",
        "modalidad": "Licitación privada",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "26/08/2026",
        "cierre": "07/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "LPR-SIT-013-2026",
        "institucion": "SIT",
        "descripcion": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO DE 4000 PSI, COMUNIDAD DE LA CUBANA...",
        "objeto": "PAVIMENTACIÓN CON CONCRETO HIDRÁULICO DE 4000 PSI, COMUNIDAD DE LA CUBANA, MUNICIPIO DE SONAGUERA, DEPARTAMENTO DE COLÓN",
        "etapa": "Elaboración",
        "modalidad": "Licitación privada",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "26/08/2026",
        "cierre": "07/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
    {
        "expediente": "SIT-CDE-CO-019-2026",
        "institucion": "SIT",
        "descripcion": "SUMINISTRO E INSTALACIÓN DE REVESTIMIENTO FLEXIBLE CEMENTICIO...",
        "objeto": "SUMINISTRO E INSTALACIÓN DE REVESTIMIENTO FLEXIBLE CEMENTICIO TIPO GEOMANTA DE CONCRETO PARA PROTECCIÓN DE BORDOS",
        "etapa": "Elaboración",
        "modalidad": "Contratación directa",
        "tipo_licitacion": "licitacion",
        "fecha_inicio": "31/08/2026",
        "cierre": "04/09/2026",
        "contacto": "licitaciones@sit.gob.hn",
        "monto": 0,
        "estado_proceso": "vigente",
    },
]

def cargar_licitaciones():
    """Carga licitaciones actuales"""
    try:
        with open("data/licitaciones.json", "r") as f:
            return json.load(f)
    except:
        return {"metadata": {}, "procesos": []}

def agregar_procesos_nuevos():
    """Agrega procesos nuevos evitando duplicados"""
    datos = cargar_licitaciones()
    procesos_actuales = datos.get("procesos", [])

    # Expedientes existentes
    expedientes_existentes = {p.get("expediente", "").strip() for p in procesos_actuales}

    agregados = 0
    duplicados = 0

    for proceso in nuevos_procesos:
        exp_limpio = proceso.get("expediente", "").strip()

        if exp_limpio in expedientes_existentes:
            duplicados += 1
            continue

        # Calcular días para cierre
        try:
            fecha_cierre = datetime.strptime(proceso["cierre"], "%d/%m/%Y")
            hoy = datetime.now()
            dias = (fecha_cierre - hoy).days
            proceso["dias_para_cierre"] = dias
        except:
            proceso["dias_para_cierre"] = 0

        proceso["fecha_extraccion"] = datetime.now().strftime("%Y-%m-%d")
        proceso["link"] = ""
        proceso["nro"] = len(procesos_actuales) + agregados + 1

        procesos_actuales.append(proceso)
        expedientes_existentes.add(exp_limpio)
        agregados += 1

    # Actualizar metadata
    datos["procesos"] = procesos_actuales
    datos["metadata"]["total_procesos"] = len(procesos_actuales)
    datos["metadata"]["fecha_actualizacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar
    with open("data/licitaciones.json", "w") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

    print(f"""
✅ Importación completada:
   ✓ Procesos agregados: {agregados}
   ⚠️  Procesos duplicados: {duplicados}
   📊 Total procesos: {len(procesos_actuales)}
    """)

if __name__ == "__main__":
    agregar_procesos_nuevos()
