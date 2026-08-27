#!/usr/bin/env python3
"""
Generador de reportes HTML a partir de datos JSON
Crea reportes interactivos para licitaciones y compras menores
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

class GeneradorReportes:
    """Genera reportes HTML desde datos JSON"""

    def __init__(self):
        self.estilos = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; padding: 20px; }
        .container { max-width: 1600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%); color: white; padding: 40px 30px; text-align: center; }
        .header h1 { font-size: 32px; margin-bottom: 10px; font-weight: 600; }
        .header p { font-size: 16px; opacity: 0.95; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; padding: 30px; background: linear-gradient(to bottom, #f8f9fa, #fff); border-bottom: 1px solid #e0e0e0; }
        .stat-box { background: white; padding: 20px; border-radius: 8px; border-left: 5px solid #1a73e8; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .stat-box h3 { color: #1a73e8; font-size: 24px; font-weight: 700; margin-bottom: 5px; }
        .stat-box p { font-size: 13px; color: #666; font-weight: 500; }
        .filters { padding: 20px 30px; background: #f8f9fa; border-bottom: 1px solid #ddd; display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
        .filters input, .filters select { padding: 10px 15px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        .filters button { padding: 10px 20px; background: #1a73e8; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: 0.3s; }
        .filters button:hover { background: #0d47a1; }
        .filters button.limpiar { background: #999; }
        .filters button.limpiar:hover { background: #666; }
        .table-wrapper { padding: 30px; overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        thead { background: #1a73e8; color: white; position: sticky; top: 0; }
        th { padding: 15px; text-align: left; font-weight: 600; border-bottom: 2px solid #0d47a1; }
        td { padding: 12px 15px; border-bottom: 1px solid #e0e0e0; }
        tr:hover { background: #f0f4ff; }
        .nro { color: #1a73e8; font-weight: 700; text-align: center; width: 50px; }
        .expediente { font-family: 'Courier New', monospace; font-weight: 600; color: #0d47a1; font-size: 12px; }
        .monto { color: #0d47a1; font-weight: 700; text-align: right; }
        .link-btn { display: inline-block; padding: 6px 12px; background: #1a73e8; color: white; text-decoration: none; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .link-btn:hover { background: #0d47a1; }
        .email-link { color: #1a73e8; text-decoration: none; font-weight: 500; }
        .email-link:hover { text-decoration: underline; }
        .results-info { padding: 15px 30px; background: #f8f9fa; font-size: 14px; color: #666; border-bottom: 1px solid #ddd; }
        .vigente { color: #059669; font-weight: 600; }
        .cerrada { color: #dc2626; font-weight: 600; }
        .footer { padding: 20px 30px; background: #f8f9fa; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #ddd; }
        .oculto { display: none; }
        """

    def generar_html_licitaciones(self, datos: Dict[str, Any], archivo_salida: str):
        """Genera HTML para licitaciones normales"""
        metadata = datos['metadata']
        procesos = datos['procesos']

        instituciones = sorted(set(p['institucion'] for p in procesos))

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Honduras Compras - Licitaciones Normales 2026</title>
    <style>
        {self.estilos}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Honduras Compras - Licitaciones Normales</h1>
            <p>Procesos de Mayor Cuantía | Instituciones Públicas 2026</p>
        </div>

        <div class="stats">
            <div class="stat-box">
                <h3>{metadata['total_procesos']}</h3>
                <p>Total Procesos</p>
            </div>
            <div class="stat-box">
                <h3>L. {metadata['inversion_total']/1e6:.1f}M</h3>
                <p>Inversión Total</p>
            </div>
            <div class="stat-box">
                <h3>L. {metadata['inversion_total']/metadata['total_procesos']/1e6:.1f}M</h3>
                <p>Promedio por Proceso</p>
            </div>
            <div class="stat-box">
                <h3>{len([p for p in procesos if p.get('estado_proceso') == 'vigente'])}</h3>
                <p>Procesos Vigentes</p>
            </div>
        </div>

        <div class="filters">
            <input type="text" id="search" placeholder="🔍 Buscar expediente, descripción..." style="flex: 1; min-width: 250px;">
            <select id="institucion">
                <option value="">📦 Todas las instituciones</option>
                {''.join(f'<option value="{i}">{i}</option>' for i in instituciones)}
            </select>
            <button onclick="filtrar()">🔎 Filtrar</button>
            <button class="limpiar" onclick="limpiar()">✕ Limpiar</button>
        </div>

        <div class="results-info">
            Mostrando <strong id="count">{len(procesos)}</strong> de <strong>{len(procesos)}</strong> procesos
        </div>

        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th style="width: 50px;">Nro</th>
                        <th style="width: 160px;">Expediente</th>
                        <th style="width: 200px;">Descripción</th>
                        <th style="width: 110px;">Institución</th>
                        <th style="width: 85px;">Inicio</th>
                        <th style="width: 85px;">Cierre</th>
                        <th style="width: 100px;">Inversión</th>
                        <th style="width: 120px;">Contacto</th>
                    </tr>
                </thead>
                <tbody id="datos"></tbody>
            </table>
        </div>

        <div class="footer">
            <p>Datos actualizados: {metadata['fecha_actualizacion']} | Fuente: SICC Honduras Compras</p>
        </div>
    </div>

    <script>
        const procesos = {json.dumps(procesos, ensure_ascii=False)};

        function renderTable(items = procesos) {{
            const tbody = document.getElementById('datos');
            tbody.innerHTML = '';

            items.forEach((p, idx) => {{
                const fila = document.createElement('tr');
                fila.innerHTML = `
                    <td class="nro">${{idx + 1}}</td>
                    <td class="expediente">${{p.expediente}}</td>
                    <td>${{p.descripcion}}</td>
                    <td><strong>${{p.institucion || 'VARIAS'}}</strong></td>
                    <td><small>${{p.fecha_inicio || 'N/A'}}</small></td>
                    <td><small>${{p.cierre}}</small></td>
                    <td class="monto">L. ${{p.monto.toLocaleString('es-HN')}}</td>
                    <td>${{p.contacto ? `<a href="mailto:${{p.contacto}}" class="email-link">📧</a>` : '-'}}</td>
                `;
                tbody.appendChild(fila);
            }});

            document.getElementById('count').textContent = items.length;
        }}

        function filtrar() {{
            const search = document.getElementById('search').value.toLowerCase();
            const institucion = document.getElementById('institucion').value;

            const filtrados = procesos.filter(p => {{
                const matchSearch = p.expediente.toLowerCase().includes(search) ||
                                   p.descripcion.toLowerCase().includes(search);
                const matchInst = !institucion || p.institucion === institucion;
                return matchSearch && matchInst;
            }});

            renderTable(filtrados);
        }}

        function limpiar() {{
            document.getElementById('search').value = '';
            document.getElementById('institucion').value = '';
            renderTable();
        }}

        // Inicializar tabla
        renderTable();

        // Buscar en tiempo real
        document.getElementById('search').addEventListener('keyup', filtrar);
        document.getElementById('institucion').addEventListener('change', filtrar);
    </script>
</body>
</html>
"""

        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Generado: {archivo_salida}")

    def generar_html_compras_menores(self, datos: Dict[str, Any], archivo_salida: str):
        """Genera HTML para compras menores"""
        metadata = datos['metadata']
        procesos = datos['procesos']

        instituciones = sorted(set(p['institucion'] for p in procesos))

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Honduras Compras - Compras Menores 2026</title>
    <style>
        {self.estilos}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📦 Honduras Compras - Compras Menores</h1>
            <p>Procesos de Menor Cuantía | Instituciones Públicas 2026</p>
        </div>

        <div class="stats">
            <div class="stat-box">
                <h3>{metadata['total_procesos']}</h3>
                <p>Total Procesos</p>
            </div>
            <div class="stat-box">
                <h3>L. {metadata['inversion_total']/1e6:.2f}M</h3>
                <p>Inversión Total</p>
            </div>
            <div class="stat-box">
                <h3>L. {metadata['inversion_total']/metadata['total_procesos']/1e3:.0f}K</h3>
                <p>Promedio por Proceso</p>
            </div>
            <div class="stat-box">
                <h3>{len([p for p in procesos if p.get('estado_proceso') == 'vigente'])}</h3>
                <p>Procesos Vigentes</p>
            </div>
        </div>

        <div class="filters">
            <input type="text" id="search" placeholder="🔍 Buscar expediente, descripción..." style="flex: 1; min-width: 250px;">
            <select id="institucion">
                <option value="">📦 Todas las instituciones</option>
                {''.join(f'<option value="{i}">{i}</option>' for i in instituciones)}
            </select>
            <button onclick="filtrar()">🔎 Filtrar</button>
            <button class="limpiar" onclick="limpiar()">✕ Limpiar</button>
        </div>

        <div class="results-info">
            Mostrando <strong id="count">{len(procesos)}</strong> de <strong>{len(procesos)}</strong> procesos
        </div>

        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th style="width: 50px;">Nro</th>
                        <th style="width: 160px;">Expediente</th>
                        <th style="width: 250px;">Descripción</th>
                        <th style="width: 130px;">Institución</th>
                        <th style="width: 100px;">Cierre</th>
                        <th style="width: 120px;">Monto</th>
                        <th style="width: 180px;">Contacto</th>
                        <th style="width: 120px;">Link SICC</th>
                    </tr>
                </thead>
                <tbody id="datos"></tbody>
            </table>
        </div>

        <div class="footer">
            <p>Datos actualizados: {metadata['fecha_actualizacion']} | Fuente: SICC Honduras Compras | Rango: L. 75K - L. 250K</p>
        </div>
    </div>

    <script>
        const procesos = {json.dumps(procesos, ensure_ascii=False)};

        function renderTable(items = procesos) {{
            const tbody = document.getElementById('datos');
            tbody.innerHTML = '';

            items.forEach((p, idx) => {{
                const fila = document.createElement('tr');
                fila.innerHTML = `
                    <td class="nro">${{idx + 1}}</td>
                    <td class="expediente">${{p.expediente}}</td>
                    <td>${{p.descripcion}}</td>
                    <td><strong>${{p.institucion || 'VARIAS'}}</strong></td>
                    <td><small>${{p.fecha_inicio || 'N/A'}}</small></td>
                    <td><small>${{p.cierre}}</small></td>
                    <td class="monto">L. ${{p.monto.toLocaleString('es-HN')}}</td>
                    <td>${{p.contacto ? `<a href="mailto:${{p.contacto}}" class="email-link">📧</a>` : '-'}}</td>
                `;
                tbody.appendChild(fila);
            }});

            document.getElementById('count').textContent = items.length;
        }}

        function filtrar() {{
            const search = document.getElementById('search').value.toLowerCase();
            const institucion = document.getElementById('institucion').value;

            const filtrados = procesos.filter(p => {{
                const matchSearch = p.expediente.toLowerCase().includes(search) ||
                                   p.descripcion.toLowerCase().includes(search);
                const matchInst = !institucion || p.institucion === institucion;
                return matchSearch && matchInst;
            }});

            renderTable(filtrados);
        }}

        function limpiar() {{
            document.getElementById('search').value = '';
            document.getElementById('institucion').value = '';
            renderTable();
        }}

        // Inicializar tabla
        renderTable();

        // Buscar en tiempo real
        document.getElementById('search').addEventListener('keyup', filtrar);
        document.getElementById('institucion').addEventListener('change', filtrar);
    </script>
</body>
</html>
"""

        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Generado: {archivo_salida}")

def main():
    """Función principal"""
    generador = GeneradorReportes()

    # Cargar datos
    if os.path.exists('data/licitaciones.json'):
        with open('data/licitaciones.json', 'r', encoding='utf-8') as f:
            licitaciones = json.load(f)
        generador.generar_html_licitaciones(licitaciones, 'reportes/licitaciones.html')
    else:
        print("⚠️  Archivo data/licitaciones.json no encontrado")

    if os.path.exists('data/compras-menores.json'):
        with open('data/compras-menores.json', 'r', encoding='utf-8') as f:
            compras = json.load(f)
        generador.generar_html_compras_menores(compras, 'reportes/compras-menores.html')
    else:
        print("⚠️  Archivo data/compras-menores.json no encontrado")

    print("\n✅ Reportes HTML generados exitosamente")

if __name__ == "__main__":
    main()
