import yaml
from pathlib import Path

# Ruta al directorio del script actual
base_path = Path(__file__).parent

# Ruta al archivo YAML relativa al script
yaml_path = base_path / "taxonomia_glaciares_completa.yaml"

# Leer el archivo YAML
with open(yaml_path, "r", encoding="utf-8") as f:
    taxonomy = yaml.safe_load(f)

# Función recursiva para construir el HTML
def render_taxonomy(tax, level=0):
    html = ""
    indent = "    " * level
    for key, value in tax.items():
        nombre = value.get("nombre", "")
        html += f"{indent}<div class='nivel' style='margin-left:{level * 20}px'><strong>{key}: {nombre}</strong></div>\n"
        if "criterios" in value:
            for criterio in value["criterios"]:
                c_nombre = criterio["nombre"]
                c_desc = criterio["descripcion"]
                html += (
                    f"{indent}<div class='criterio' style='margin-left:{(level + 1) * 20}px'>"
                    f"<label><input type='checkbox' name='criterio' value='{c_nombre}'>"
                    f" <strong>{c_nombre}</strong> – <em>{c_desc}</em></label></div>\n"
                )
        for subkey, subvalue in value.items():
            if isinstance(subvalue, dict) and "nombre" in subvalue:
                html += render_taxonomy({subkey: subvalue}, level + 1)
    return html

# Estructura base del HTML
html_head = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Taxonomía de Evaluación de Glaciares</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 20px; }
        .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .nivel { margin-top: 10px; font-weight: bold; }
        .criterio { margin-top: 5px; }
        input[type="checkbox"] { margin-right: 8px; }
        #taxonomia { display: none; margin-top: 20px; }
    </style>
    <script>
        function toggleTaxonomia() {
            var section = document.getElementById("taxonomia");
            var button = document.getElementById("toggleButton");
            if (section.style.display === "none") {
                section.style.display = "block";
                button.textContent = "Ocultar Taxonomía";
            } else {
                section.style.display = "none";
                button.textContent = "Mostrar Taxonomía";
            }
        }
    </script>
</head>
<body>
<div class="container">
<h2>Taxonomía de Evaluación de Glaciares</h2>
<button id="toggleButton" onclick="toggleTaxonomia()">Mostrar Taxonomía</button>
<div id="taxonomia">
<form>
"""

html_footer = """
</form>
</div> <!-- Cierre de #taxonomia -->
</div> <!-- Cierre de .container -->
</body>
</html>
"""

# Generar HTML completo
html_body = render_taxonomy(taxonomy)
html_content = html_head + html_body + html_footer

# Guardar en archivo
output_file = Path(__file__).parent / "taxonomia_glaciares_seleccion.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ HTML generado: taxonomia_glaciares_seleccion.html")
