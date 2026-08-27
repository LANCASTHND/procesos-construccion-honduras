#!/usr/bin/env python3
"""
Script de diagnóstico para SICC Honduras Compras
Ayuda a entender la estructura y parámetros correctos
"""

import requests
from bs4 import BeautifulSoup
import json
import time

def diagnosticar_sicc():
    """Diagnostica cómo funciona SICC"""

    url = "http://sicc.honducompras.gob.hn/HC/procesos/busquedahistorico.aspx"

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    print("="*70)
    print("🔍 DIAGNÓSTICO SICC HONDURAS COMPRAS")
    print("="*70)

    # Paso 1: Obtener la página inicial
    print("\n[1] Descargando página inicial...")
    try:
        response = session.get(url, timeout=15)
        response.encoding = 'utf-8'
        print(f"✅ Estado: {response.status_code}")
        print(f"   Tamaño: {len(response.content)} bytes")
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Paso 2: Analizar elementos de formulario
    print("\n[2] Analizando elementos del formulario...")
    soup = BeautifulSoup(response.content, 'html.parser')

    # Buscar tokens ASP.NET
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})
    eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})

    print(f"   __VIEWSTATE: {'✅ Encontrado' if viewstate else '❌ No encontrado'}")
    print(f"   __EVENTVALIDATION: {'✅ Encontrado' if eventvalidation else '❌ No encontrado'}")

    # Buscar dropdowns
    print("\n[3] Buscando dropdowns de institución...")
    dropdowns_inst = soup.find_all('select', {'id': lambda x: x and 'Institucion' in x if x else False})
    print(f"   Dropdowns encontrados: {len(dropdowns_inst)}")

    if dropdowns_inst:
        for dd in dropdowns_inst:
            print(f"   - ID: {dd.get('id')}, Name: {dd.get('name')}")
            opciones = dd.find_all('option')
            print(f"     Opciones: {len(opciones)}")
            if len(opciones) <= 20:
                for opt in opciones[:10]:
                    print(f"       • {opt.get('value')} - {opt.text}")

    # Paso 3: Verificar tabla de resultados
    print("\n[4] Buscando tabla de resultados...")
    tablas = soup.find_all('table')
    print(f"   Total de tablas: {len(tablas)}")

    for idx, tabla in enumerate(tablas[:3]):
        filas = tabla.find_all('tr')
        print(f"   Tabla {idx}: {len(filas)} filas")
        if filas and len(filas) > 0:
            celdas_header = filas[0].find_all(['th', 'td'])
            print(f"     Encabezado: {[c.text.strip() for c in celdas_header[:5]]}")

    # Paso 4: Intentar búsqueda simple (SIN filtro)
    print("\n[5] Intentando búsqueda general (sin filtro de institución)...")
    time.sleep(1)

    try:
        data = {
            '__VIEWSTATE': viewstate.get('value', '') if viewstate else '',
            '__EVENTVALIDATION': eventvalidation.get('value', '') if eventvalidation else '',
            'ctl00$ContentPlaceHolder1$btnBuscar': 'Buscar',
        }

        response2 = session.post(url, data=data, timeout=15)
        response2.encoding = 'utf-8'
        print(f"✅ POST realizado - Status: {response2.status_code}")
        print(f"   Tamaño respuesta: {len(response2.content)} bytes")

        soup2 = BeautifulSoup(response2.content, 'html.parser')
        tablas2 = soup2.find_all('table')
        print(f"   Tablas en respuesta: {len(tablas2)}")

        # Buscar resultados
        for tabla in tablas2:
            filas = tabla.find_all('tr')
            if len(filas) > 2:  # Header + datos
                print(f"   Encontrada tabla con {len(filas)} filas")
                for idx, fila in enumerate(filas[1:4]):  # Mostrar primeras 3 filas
                    celdas = fila.find_all('td')
                    if celdas:
                        print(f"     Fila {idx+1}: {[c.text.strip()[:30] for c in celdas[:3]]}")
                break

    except Exception as e:
        print(f"❌ Error: {e}")

    # Paso 5: Intentar búsqueda con institución específica (UNAH)
    print("\n[6] Intentando búsqueda con institución (UNAH)...")
    time.sleep(1)

    try:
        # Primero obtener tokens actualizados
        response_fresh = session.get(url, timeout=15)
        soup_fresh = BeautifulSoup(response_fresh.content, 'html.parser')
        viewstate_fresh = soup_fresh.find('input', {'name': '__VIEWSTATE'})
        eventval_fresh = soup_fresh.find('input', {'name': '__EVENTVALIDATION'})

        data_inst = {
            '__VIEWSTATE': viewstate_fresh.get('value', '') if viewstate_fresh else '',
            '__EVENTVALIDATION': eventval_fresh.get('value', '') if eventval_fresh else '',
            'ctl00$ContentPlaceHolder1$ddlInstitucion': 'UNAH',
            'ctl00$ContentPlaceHolder1$btnBuscar': 'Buscar',
        }

        response3 = session.post(url, data=data_inst, timeout=15)
        response3.encoding = 'utf-8'
        print(f"✅ POST con institución - Status: {response3.status_code}")

        soup3 = BeautifulSoup(response3.content, 'html.parser')

        # Buscar cualquier tabla con datos
        for tabla in soup3.find_all('table'):
            filas = tabla.find_all('tr')
            if len(filas) > 2:
                print(f"   Tabla encontrada: {len(filas)} filas")
                for fila in filas[1:4]:
                    celdas = fila.find_all('td')
                    if celdas and len(celdas) > 0:
                        print(f"     {[c.text.strip()[:30] for c in celdas[:3]]}")
                break
        else:
            print("   ⚠️  No se encontraron tablas con datos")

    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "="*70)
    print("✅ Diagnóstico completado")
    print("="*70)

if __name__ == "__main__":
    diagnosticar_sicc()
