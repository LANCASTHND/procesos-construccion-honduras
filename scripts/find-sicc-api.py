#!/usr/bin/env python3
"""
Script para encontrar endpoints de API JSON en SICC
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def buscar_api_sicc():
    """Busca posibles endpoints JSON en SICC"""

    print("="*70)
    print("🔍 Buscando endpoints de API en SICC")
    print("="*70 + "\n")

    base_url = "http://sicc.honducompras.gob.hn"

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    # Posibles endpoints de API
    endpoints_posibles = [
        "/api/procesos",
        "/api/licitaciones",
        "/api/compras",
        "/API/procesos",
        "/HC/api/procesos",
        "/HC/API/procesos",
        "/HC/services/procesos",
        "/HC/webservices/procesos",
        "/Services/ProcesosService.asmx",
        "/WebServices/ProcesosService.asmx",
        "/data/licitaciones.json",
        "/data/procesos.json",
        "/json/licitaciones",
        "/api/v1/procesos",
        "/api/v2/procesos",
    ]

    print("[1] Probando endpoints comunes de API...\n")

    for endpoint in endpoints_posibles:
        url = base_url + endpoint
        try:
            response = session.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Status: {response.status_code}")
                if 'json' in response.headers.get('content-type', '').lower():
                    print(f"   Content-Type: JSON ✅")
                    data = response.json()
                    print(f"   Estructura: {list(data.keys())[:5]}")
                elif '<html' in response.text.lower():
                    print(f"   Content-Type: HTML ❌")
                else:
                    print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        except requests.exceptions.RequestException:
            pass
        except Exception as e:
            pass

    # Buscar referencias a API en el HTML
    print("\n[2] Buscando referencias de API en página principal...\n")

    try:
        response = session.get(base_url + "/HC/procesos/busquedahistorico.aspx", timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar scripts
        scripts = soup.find_all('script', src=True)
        print(f"Scripts externos encontrados: {len(scripts)}")
        for script in scripts[:5]:
            print(f"  - {script.get('src')}")

        # Buscar referencias a AJAX/fetch
        all_scripts = soup.find_all('script')
        print(f"\nScripts inline encontrados: {len(all_scripts)}")

        for script in all_scripts:
            if script.string:
                # Buscar URLs de API
                urls = re.findall(r'(?:url|URL|uri|endpoint).*?["\'](/[^"\']*)["\']', script.string)
                if urls:
                    print(f"  URLs encontradas:")
                    for url in set(urls):
                        print(f"    - {url}")

                # Buscar JSON
                if '.json' in script.string or 'json' in script.string.lower():
                    print(f"  ✅ Referencia a JSON en script")

    except Exception as e:
        print(f"Error: {e}")

    # Probar búsqueda con ajax
    print("\n[3] Probando peticiones AJAX/WebService...\n")

    ajax_endpoints = [
        ("/HC/procesos/busquedahistorico.aspx/ObtenerProcesos", "POST"),
        ("/HC/procesos/busquedahistorico.aspx/GetProcesos", "POST"),
        ("/WebService.asmx/GetProcesos", "POST"),
    ]

    for endpoint, metodo in ajax_endpoints:
        url = base_url + endpoint
        try:
            if metodo == "POST":
                response = session.post(url, json={}, timeout=5)
            else:
                response = session.get(url, timeout=5)

            if response.status_code != 404:
                print(f"✅ {endpoint} - Status: {response.status_code}")
                if response.text:
                    print(f"   Response preview: {response.text[:100]}")
        except:
            pass

    print("\n" + "="*70)

if __name__ == "__main__":
    buscar_api_sicc()
