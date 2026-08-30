#!/usr/bin/env python3
"""
Generador de reporte UNGM - Procesos de Construcción y Materiales
Crea reporte interactivo a partir de datos JSON
"""

import json
import os
from datetime import datetime

class GeneradorReporteUNGM:
    """Genera reporte HTML de procesos UNGM"""

    def __init__(self):
        self.estilos = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; padding: 20px; }
        .container { max-width: 1600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #0066cc 0%, #003d99 100%); color: white; padding: 40px 30px; text-align: center; }
        .header h1 { font-size: 32px; margin-bottom: 10px; font-weight: 600; }
        .header p { font-size: 16px; opacity: 0.95; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; padding: 30px; background: linear-gradient(to bottom, #f8f9fa, #fff); border-bottom: 1px solid #e0e0e0; }
        .stat-box { background: white; padding: 20px; border-radius: 8px; border-left: 5px solid #0066cc; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .stat-box h3 { color: #0066cc; font-size: 24px; font-weight: 700; margin-bottom: 5px; }
        .stat-box p { font-size: 13px; color: #666; font-weight: 500; }
        .filters { padding: 20px 30px; background: #f8f9fa; border-bottom: 1px solid #ddd; display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
        .filters input, .filters select { padding: 10px 15px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        .filters button { padding: 10px 20px; background: #0066cc; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: 0.3s; }
        .filters button:hover { background: #003d99; }
        .filters button.limpiar { background: #999; }
        .filters button.limpiar:hover { background: #666; }
        .table-wrapper { padding: 30px; overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        thead { background: #0066cc; color: white; position: sticky; top: 0; }
        th { padding: 15px; text-align: left; font-weight: 600; border-bottom: 2px solid #003d99; }
        td { padding: 12px 15px; border-bottom: 1px solid #e0e0e0; }
        tr:hover { background: #f0f4ff; }
        .nro { color: #0066cc; font-weight: 700; text-align: center; width: 50px; }
        .link-btn { display: inline-block; padding: 6px 12px; background: #0066cc; color: white; text-decoration: none; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .link-btn:hover { background: #003d99; }
        .results-info { padding: 15px 30px; background: #f8f9fa; font-size: 14px; color: #666; border-bottom: 1px solid #ddd; }
        .footer { padding: 20px 30px; background: #f8f9fa; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #ddd; }
        .oculto { display: none; }
        """

    def generar_html(self, datos, archivo_salida):
        """Genera HTML del reporte"""
        metadata = datos['metadata']
        procesos = datos['procesos']

        paises = sorted(set(p.get('pais', 'N/A') for p in procesos if p.get('pais')))

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UNGM - Procesos de Construcción</title>
    <style>
        {self.estilos}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 UNGM - Procesos de Construcción y Materiales</h1>
            <p>Oportunidades Internacionales de Construcción | United Nations Global Marketplace</p>
        </div>

        <div class="stats">
            <div class="stat-box">
                <h3>{len(procesos)}</h3>
                <p>Total Procesos</p>
            </div>
            <div class="stat-box">
                <h3>{len(paises)}</h3>
                <p>Países</p>
            </div>
            <div class="stat-box">
                <h3>UNGM</h3>
                <p>Fuente</p>
            </div>
            <div class="stat-box">
                <h3>{metadata['fecha_actualizacion']}</h3>
                <p>Actualizado</p>
            </div>
        </div>

        <div class="filters">
            <input type="text" id="search" placeholder="🔍 Buscar referencia, título..." style="flex: 1; min-width: 250px;">
            <select id="pais">
                <option value="">🌐 Todos los países</option>
                {''.join(f'<option value="{p}">{p}</option>' for p in paises)}
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
                        <th style="width: 200px;">Referencia</th>
                        <th style="width: 350px;">Título</th>
                        <th style="width: 120px;">País</th>
                        <th style="width: 100px;">Tipo</th>
                        <th style="width: 85px;">Publicado</th>
                        <th style="width: 85px;">Cierre</th>
                        <th style="width: 100px;">Link</th>
                    </tr>
                </thead>
                <tbody id="datos"></tbody>
            </table>
        </div>

        <div class="footer">
            <p>Datos de: {metadata['fuente']} | Actualizado: {metadata['fecha_actualizacion']} | <a href="{metadata['url']}" target="_blank">Ver en UNGM</a></p>
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
                    <td><small>${{p.referencia || '—'}}</small></td>
                    <td><strong>${{p.titulo || '—'}}</strong></td>
                    <td>${{p.pais || 'N/A'}}</td>
                    <td><small>${{p.tipo || 'Construcción'}}</small></td>
                    <td>${{p.fecha_publicado || '—'}}</td>
                    <td>${{p.fecha_cierre || '—'}}</td>
                    <td><a href="${{p.url}}" target="_blank" class="link-btn">Ver</a></td>
                `;
                tbody.appendChild(fila);
            }});

            document.getElementById('count').textContent = items.length;
        }}

        function filtrar() {{
            const busqueda = document.getElementById('search').value.toLowerCase();
            const pais = document.getElementById('pais').value;

            const filtrados = procesos.filter(p => {{
                const busquedaOk = !busqueda ||
                    (p.referencia && p.referencia.toLowerCase().includes(busqueda)) ||
                    (p.titulo && p.titulo.toLowerCase().includes(busqueda));
                const paisOk = !pais || p.pais === pais;
                return busquedaOk && paisOk;
            }});

            renderTable(filtrados);
        }}

        function limpiar() {{
            document.getElementById('search').value = '';
            document.getElementById('pais').value = '';
            renderTable();
        }}

        // Renderizar tabla inicial
        renderTable();
    </script>
</body>
</html>
"""

        os.makedirs(os.path.dirname(archivo_salida) if os.path.dirname(archivo_salida) else '.', exist_ok=True)
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(html)

def main():
    """Función principal"""
    generador = GeneradorReporteUNGM()

    # Cargar datos
    with open('data/ungm-construccion.json', 'r', encoding='utf-8') as f:
        datos = json.load(f)

    # Generar reporte
    generador.generar_html(datos, 'reportes/ungm-construccion.html')
    print("✅ Generado: reportes/ungm-construccion.html")

if __name__ == '__main__':
    main()
