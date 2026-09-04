#!/usr/bin/env python3
"""
Genera reporte HTML de contactos de compradores para compras menores Honduras 2026
Mapea cada proceso de compra menor con información de contacto institucional
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def generar_reporte_contactos():
    """Genera HTML con contactos de compradores"""

    # Rutas
    data_dir = Path(__file__).parent.parent / "data"
    compras_file = data_dir / "compras-menores.json"
    instituciones_file = data_dir / "instituciones.json"
    output_file = Path(__file__).parent.parent / "reportes" / "contactos-compradores.html"

    # Cargar datos
    try:
        with open(compras_file) as f:
            compras_data = json.load(f)
        with open(instituciones_file) as f:
            instituciones_data = json.load(f)
    except Exception as e:
        print(f"❌ Error cargando archivos: {e}")
        sys.exit(1)

    # Crear mapa de instituciones
    instituciones_map = {}
    for inst in instituciones_data.get('instituciones', []):
        instituciones_map[inst['sigla']] = {
            'nombre': inst['nombre'],
            'telefono': inst['telefono'],
            'email': inst['contacto'],
            'sitio': inst.get('sitio', '')
        }

    # Procesos
    procesos = compras_data.get('procesos', [])
    metadata = compras_data.get('metadata', {})

    # Calcular estadísticas
    total_procesos = len(procesos)
    instituciones_unicas = len(set(p['institucion'] for p in procesos))
    procesos_proximosCierre = len([p for p in procesos if p.get('dias_para_cierre', 0) <= 7])

    # HTML
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contactos de Compradores - Compras Menores Honduras 2026</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --primary: #2563eb;
            --primary-light: #3b82f6;
            --primary-dark: #1e40af;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --gray-900: #111827;
            --bg: #ffffff;
            --text: #1f2937;
            --border: #e5e7eb;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg: #1f2937;
                --text: #f3f4f6;
                --border: #4b5563;
                --gray-50: #111827;
                --gray-100: #1f2937;
                --gray-200: #374151;
                --gray-600: #d1d5db;
                --gray-700: #e5e7eb;
                --gray-900: #f9fafb;
            }}
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 20px;
            transition: background-color 0.2s, color 0.2s;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--border);
        }}

        h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            color: var(--primary);
        }}

        .subtitle {{
            font-size: 14px;
            color: var(--gray-600);
            margin-top: 5px;
        }}

        .controls {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .search-box, .select-box {{
            padding: 10px 15px;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: var(--bg);
            color: var(--text);
            font-size: 14px;
        }}

        .search-box:focus, .select-box:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}

        .stat-card {{
            padding: 15px;
            background: var(--gray-50);
            border-radius: 8px;
            border-left: 4px solid var(--primary);
        }}

        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: var(--primary);
        }}

        .stat-label {{
            font-size: 12px;
            color: var(--gray-600);
            margin-top: 5px;
            text-transform: uppercase;
        }}

        .table-wrapper {{
            overflow-x: auto;
            border-radius: 8px;
            border: 1px solid var(--border);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--bg);
        }}

        thead {{
            background: var(--gray-50);
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        th {{
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            color: var(--gray-700);
            border-bottom: 2px solid var(--border);
            letter-spacing: 0.5px;
        }}

        td {{
            padding: 12px 15px;
            border-bottom: 1px solid var(--border);
            font-size: 14px;
        }}

        tbody tr:hover {{
            background: var(--gray-50);
            transition: background-color 0.2s;
        }}

        .expediente {{
            font-weight: 600;
            color: var(--primary);
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }}

        .institucion {{
            font-weight: 500;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }}

        .contacto-link {{
            color: var(--primary);
            text-decoration: none;
            font-size: 12px;
        }}

        .contacto-link:hover {{
            text-decoration: underline;
        }}

        .phone {{
            font-family: 'Courier New', monospace;
            font-weight: 500;
            color: var(--success);
        }}

        .no-data {{
            text-align: center;
            padding: 40px 20px;
            color: var(--gray-600);
        }}

        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .badge-vigente {{
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
        }}

        .badge-proximo {{
            background: rgba(245, 158, 11, 0.1);
            color: var(--warning);
        }}

        .description-cell {{
            max-width: 300px;
            white-space: normal;
            word-wrap: break-word;
        }}

        .filter-active {{
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.2) 0%, rgba(59, 130, 246, 0.1) 100%);
            border-color: var(--primary);
        }}

        .hidden {{
            display: none !important;
        }}

        .export-btn {{
            padding: 10px 15px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: background-color 0.2s;
        }}

        .export-btn:hover {{
            background: var(--primary-dark);
        }}

        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            font-size: 12px;
            color: var(--gray-600);
            text-align: center;
        }}

        .info-box {{
            background: var(--gray-50);
            border-left: 4px solid var(--warning);
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}

        .info-box strong {{
            color: var(--warning);
        }}

        @media (max-width: 768px) {{
            .controls {{
                grid-template-columns: 1fr;
            }}

            table {{
                font-size: 12px;
            }}

            th, td {{
                padding: 8px 10px;
            }}

            .description-cell {{
                max-width: 150px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Contactos de Compradores</h1>
            <p class="subtitle">Compras Menores Honduras 2026 - Información Institucional de Adquisiciones</p>
        </div>

        <div class="info-box">
            <strong>ℹ️ Información:</strong> Esta tabla muestra contactos institucionales para cada proceso de compra menor.
            Para obtener contactos de compradores individuales específicos, consulte directamente con la institución responsable.
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{total_procesos}</div>
                <div class="stat-label">Total Procesos</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{instituciones_unicas}</div>
                <div class="stat-label">Instituciones</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{procesos_proximosCierre}</div>
                <div class="stat-label">Próximos a Cerrar</div>
            </div>
        </div>

        <div class="controls">
            <div>
                <input type="text" id="searchBox" class="search-box" placeholder="🔍 Buscar por expediente...">
            </div>
            <div>
                <select id="filterInstitucion" class="select-box">
                    <option value="">Filtrar por Institución (todas)</option>
                </select>
            </div>
            <button class="export-btn" onclick="exportToCSV()">📥 Exportar CSV</button>
        </div>

        <div class="table-wrapper">
            <table id="contactosTable">
                <thead>
                    <tr>
                        <th>Expediente</th>
                        <th>Institución</th>
                        <th>Descripción</th>
                        <th>Email Institucional</th>
                        <th>Teléfono</th>
                        <th>Cierre</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    <tr>
                        <td colspan="7" class="no-data">Cargando datos...</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>Datos actualizados: <span id="dataFecha">{metadata.get('fecha_actualizacion', '--')}</span></p>
            <p>Sistema de Reportes Interactivos - Procesos de Construcción Honduras 2026</p>
            <p><a href="https://github.com/LANCASTHND/procesos-construccion-honduras" target="_blank">📌 Ver repositorio</a></p>
        </div>
    </div>

    <script>
        let allData = [];
        let filteredData = [];

        // Datos embebidos
        const institucionesMap = {json.dumps(instituciones_map)};

        const procesos = {json.dumps(procesos)};

        function loadData() {{
            try {{
                allData = procesos.map(proceso => {{
                    const instInfo = institucionesMap[proceso.institucion] || {{
                        nombre: proceso.institucion,
                        telefono: 'N/A',
                        email: proceso.contacto,
                        sitio: ''
                    }};

                    return {{
                        ...proceso,
                        institucionInfo: instInfo,
                        proximoCierre: proceso.dias_para_cierre <= 7
                    }};
                }});

                updateStats();
                renderTable(allData);
                populateFilters();
            }} catch (error) {{
                console.error('Error cargando datos:', error);
                document.getElementById('tableBody').innerHTML = '<tr><td colspan="7" class="no-data">Error al cargar datos</td></tr>';
            }}
        }}

        function updateStats() {{
            const totalProcesos = allData.length;
            // Stats ya calculados en Python
        }}

        function populateFilters() {{
            const instituciones = [...new Set(allData.map(p => p.institucion))].sort();
            const select = document.getElementById('filterInstitucion');

            instituciones.forEach(inst => {{
                const option = document.createElement('option');
                option.value = inst;
                option.textContent = inst;
                select.appendChild(option);
            }});
        }}

        function renderTable(data) {{
            const tbody = document.getElementById('tableBody');

            if (data.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="7" class="no-data">No hay datos que coincidan con los filtros</td></tr>';
                return;
            }}

            tbody.innerHTML = data.map(proceso => `
                <tr>
                    <td><span class="expediente">${{proceso.expediente}}</span></td>
                    <td><span class="institucion">${{proceso.institucion}}</span></td>
                    <td class="description-cell">${{proceso.descripcion}}</td>
                    <td><a href="mailto:${{proceso.institucionInfo.email}}" class="contacto-link">${{proceso.institucionInfo.email}}</a></td>
                    <td><span class="phone">${{proceso.institucionInfo.telefono}}</span></td>
                    <td>${{proceso.cierre}}</td>
                    <td>
                        ${{proceso.proximoCierre
                            ? `<span class="badge badge-proximo">⚠️ Próximo</span>`
                            : `<span class="badge badge-vigente">✓ Vigente</span>`}}
                    </td>
                </tr>
            `).join('');
        }}

        function applyFilters() {{
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const institucionFilter = document.getElementById('filterInstitucion').value;

            filteredData = allData.filter(proceso => {{
                const matchSearch = !searchTerm ||
                    proceso.expediente.toLowerCase().includes(searchTerm) ||
                    proceso.descripcion.toLowerCase().includes(searchTerm) ||
                    proceso.institucion.toLowerCase().includes(searchTerm);

                const matchInstitucion = !institucionFilter || proceso.institucion === institucionFilter;

                return matchSearch && matchInstitucion;
            }});

            renderTable(filteredData);
        }}

        function exportToCSV() {{
            const data = filteredData.length > 0 ? filteredData : allData;

            const headers = ['Expediente', 'Institución', 'Descripción', 'Email', 'Teléfono', 'Cierre', 'Días para Cierre'];
            const rows = data.map(p => [
                p.expediente,
                p.institucion,
                p.descripcion,
                p.institucionInfo.email,
                p.institucionInfo.telefono,
                p.cierre,
                p.dias_para_cierre
            ]);

            let csv = headers.join(',') + '\\n';
            csv += rows.map(row => row.map(cell => `"${{cell}}"`).join(',')).join('\\n');

            const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', `contactos-compradores-${{new Date().toISOString().split('T')[0]}}.csv`);
            link.click();
        }}

        // Event listeners
        document.getElementById('searchBox').addEventListener('input', applyFilters);
        document.getElementById('filterInstitucion').addEventListener('change', applyFilters);

        // Cargar datos al iniciar
        loadData();
    </script>
</body>
</html>
"""

    # Guardar
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Reporte generado: {output_file}")
        print(f"   📊 Total procesos: {total_procesos}")
        print(f"   🏛️  Instituciones: {instituciones_unicas}")
        print(f"   ⚠️  Próximos a cerrar: {procesos_proximosCierre}")

    except Exception as e:
        print(f"❌ Error guardando reporte: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generar_reporte_contactos()
