import pandas as pd
import geopandas as gpd
import folium
import numpy as np
from shapely.geometry import Point
from folium import Element

# === PARTE 1: CARGAR DATOS DE GLACIARES ===
df = pd.read_csv('data/glaciares.csv', sep=';', encoding='ISO-8859-1')
# df = pd.read_csv('data/glaciares.csv', sep=';', encoding='ISO-8859-1')
df.columns = df.columns.str.strip().str.lower()

# Convertir columnas numéricas a tipo adecuado
for col in df.columns:
    if col not in ['lat', 'lon', 'nombre_glaciar']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Crear GeoDataFrame
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df['lon'], df['lat']),
    crs="EPSG:4326"
)


# === PARTE 2: FUNCIÓN PROMETHEE II (Tipo V) ===
def preference_function_type_v(d, q, p):
    if d <= q:
        return 0
    elif d > p:
        return 1
    else:
        return (d - q) / (p - q)


def compute_preference_matrix(data, weights, q_vals, p_vals):
    n, m = data.shape
    preference_matrix = np.zeros((n, n))
    for i in range(n):
        for k in range(n):
            if i == k:
                continue
            preference_score = 0
            for j in range(m):
                diff = data[i, j] - data[k, j]
                pj = preference_function_type_v(diff, q_vals[j], p_vals[j])
                preference_score += weights[j] * pj
            preference_matrix[i, k] = preference_score
    return preference_matrix


def compute_flows(preference_matrix):
    n = preference_matrix.shape[0]
    phi_plus = np.sum(preference_matrix, axis=1) / (n - 1)
    phi_minus = np.sum(preference_matrix, axis=0) / (n - 1)
    phi = phi_plus - phi_minus
    return phi_plus, phi_minus, phi


# === PARTE 3: APLICAR PROMETHEE A LOS GLACIARES ===
criterios = [col for col in df.columns if col not in ['lat', 'lon', 'nombre_glaciar']]

data = gdf[criterios].to_numpy()


# Generar pesos y umbrales automáticamente según cantidad de criterios
num_criterios = len(criterios)
pesos = np.full(num_criterios, 1 / num_criterios)  # pesos iguales
q_vals = np.full(num_criterios, 0.5)               # valor q por defecto
p_vals = np.full(num_criterios, 5.0)               # valor p por defecto

pref_matrix = compute_preference_matrix(data, pesos, q_vals, p_vals)
phi_plus, phi_minus, phi = compute_flows(pref_matrix)

gdf['phi_plus'] = phi_plus
gdf['phi_minus'] = phi_minus
gdf['riesgo'] = phi

ranking = pd.DataFrame({
    'Glaciar': gdf['nombre_glaciar'],
    'Phi+ (Positivo)': phi_plus,
    'Phi- (Negativo)': phi_minus,
    'Phi (Neto)': phi
}).sort_values(by='Phi (Neto)', ascending=False).reset_index(drop=True)

print("\n📊 Ranking de glaciares según PROMETHEE II:\n")
print(ranking.to_string(index=True))

# === PARTE 4: MAPA CON PANEL INTERACTIVO ===
map_center = [-33.6, -70.2]
m = folium.Map(location=map_center, zoom_start=10)


def color_por_riesgo(score):
    if score < 0:
        return 'red'
    elif score < 0.29:
        return 'orange'
    else:
        return 'green'


for _, fila in gdf.iterrows():
    lat = fila.geometry.y
    lon = fila.geometry.x
    if pd.isna(lat) or pd.isna(lon):
        continue
    if not (-39 <= lat <= -33) or not (-74 <= lon <= -70):
        continue

    color = color_por_riesgo(fila['riesgo'])

    folium.Circle(
        location=[lat, lon],
        radius=1500,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        popup=folium.Popup(
            f"<b>{fila['nombre_glaciar']}</b><br>Riesgo (φ): {fila['riesgo']:.3f}<br>Φ⁺: {fila['phi_plus']:.3f}<br>Φ⁻: {fila['phi_minus']:.3f}",
            max_width=300
        )
    ).add_to(m)

# === PANEL TAXONOMÍA COMPLETA CON CRITERIOS USADOS RESALTADOS ===
criterios_usados = {
    'pendiente': 'Pendiente de la Lengua del Glaciar',
    'volumen': 'Volumen del Glaciar',
    'proximidad_lago': 'Distancia entre el Término del Glaciar y el Lago'
}


def resaltar(texto):
    return f"<span style='color:green; font-weight:bold;'>{texto}</span>"


def marcar_criterio(nombre):
    for v in criterios_usados.values():
        if nombre.strip().lower() == v.strip().lower():
            return resaltar(nombre)
    return nombre


# --- Bloque de estilo CSS (sin errores de inyección) ---
style_html = """
<style>
  .resaltado {
    color: green;
    font-weight: bold;
  }
  .taxonomia-box {
    background-color: #f9f9f9;
    border: 1px solid #ccc;
    padding: 10px;
    max-height: 300px;
    overflow-y: auto;
    font-family: Arial, sans-serif;
    font-size: 14px;
  }
  #toggleTaxonomia {
    margin-top: 10px;
    padding: 8px 12px;
    background-color: #006837;
    color: white;
    border: none;
    cursor: pointer;
  }
</style>
"""
m.get_root().html.add_child(Element(style_html))


taxonomia_html = """
<button onclick="toggleTaxonomia()" style="position: fixed; top: 30px; right: 20px; z-index:9999;
    background-color: #007bff; color: white; border: none; padding: 8px 14px; cursor: pointer;
    font-size: 13px; border-radius: 5px; box-shadow: 1px 1px 4px rgba(0,0,0,0.2);">
    Mostrar/Ocultar Taxonomía
</button>

<div id="taxonomiaPanel" style="position: fixed; top: 70px; right: 20px; width: 400px; max-height: 500px;
    overflow-y: auto; background-color: white; border: 2px solid #888; padding: 12px; z-index: 9999;
    font-size: 13px; display: none; box-shadow: 2px 2px 8px rgba(0,0,0,0.3); border-radius: 6px;">
  <h2>Taxonomía de Evaluación de Glaciares</h2>
  <ul>
    <li><b>A:</b> Características del Glaciar Padre
      <ul>
        <li><b>A.1:</b> Geometría del Glaciar
          <ul>
            <li><b>A.1.a:</b> Tamaño
              <ul>
                <li><b>Área del Glaciar Padre</b>: Un área mayor puede implicar un mayor volumen de hielo</li>
                <li><b>Volumen</b>: Inferido de 'Área' y 'Espesor'</li>
                <li><b>Longitud del Glaciar</b>: Considerado en la selección de lagos potencialmente peligrosos</li>
                <li><b>Ancho</b>: Considerado en la selección de lagos potencialmente peligrosos</li>
              </ul>
            </li>
            <li><b>A.1.b:</b> Morfología y Pendiente
              <ul>
                <li><b>Pendiente</b>: Una pendiente pronunciada puede aumentar la probabilidad de avalanchas de hielo</li>
                <li><b>Presencia de Grietas (Crevasses)</b>: Pueden indicar inestabilidad y ser puntos de desprendimiento de avalanchas</li>
              </ul>
            </li>
          </ul>
        </li>
        <li><b>A.2:</b> Ubicación y Elevación
          <ul>
            <li><b>Elevación del Glaciar Madre</b>: Influye en las condiciones climáticas y la tasa de fusión del hielo</li>
            <li><b>Orientación del Glaciar (Aspecto)</b>: Puede influir en la radiación solar recibida y la tasa de fusión</li>
          </ul>
        </li>
        <li><b>A.3:</b> Subsuelo Glaciar
          <ul>
            <li><b>Topografía Subglacial (Bed Topography)</b>: La presencia de sobre-profundizaciones crea sitios favorables para la formación de lagos</li>
            <li><b>Espesor del Hielo</b>: Crucial para estimar la topografía subglacial y la posibilidad de formación de depresiones</li>
          </ul>
        </li>
      </ul>
    </li>
    <li><b>B:</b> Dinámica y Comportamiento Glaciar
      <ul>
        <li><b>B.1:</b> Estado y Cambios del Glaciar
          <ul>
            <li><b>Retroceso Glaciar</b>: Lleva a la formación y expansión de lagos proglaciales</li>
            <li><b>Avance Glaciar (Surge)</b>: Puede bloquear el drenaje y formar lagos represados por hielo</li>
            <li><b>Tasa de Expansión/Retroceso</b>: Indica la rapidez de los cambios y el potencial de formación o crecimiento de lagos</li>
          </ul>
        </li>
        <li><b>B.2:</b> Procesos Activos
          <ul>
            <li><b>Actividad de Avalanchas de Hielo</b>: Pueden alcanzar lagos y desencadenar GLOFs</li>
            <li><b>Velocidad de Flujo del Glaciar</b>: Velocidades extremas pueden indicar inestabilidad</li>
            <li><b>Fusión del Hielo (Snow/Ice Melt Water)</b>: El aumento puede incrementar el nivel de los lagos y la presión sobre las represas</li>
          </ul>
        </li>
      </ul>
    </li>
    <li><b>C:</b> Interacción Glaciar - Lago Glaciar
      <ul>
        <li><b>C.1:</b> Proximidad
          <ul>
            <li><b>Proximidad al Lago</b>: Menor distancia aumenta la probabilidad de impacto</li>
            <li><b>Contacto Glaciar-Lago</b>: El contacto directo aumenta la susceptibilidad a GLOFs</li>
          </ul>
        </li>
        <li><b>C.2:</b> Conexión
          <ul>
            <li><b>Conexión Hidrológica</b>: La existencia de conexión directa influye en la dinámica del lago</li>
            <li><b>Tipo de Lago Glaciar</b>: Proglacial (conectado), desconectado, supraglaciar</li>
          </ul>
        </li>
      </ul>
    </li>
    <li><b>D:</b> Susceptibilidad a Desprendimientos de Masa
      <ul>
        <li><b>D.1:</b> Terreno Adyacente
          <ul>
            <li><b>Pendiente del Terreno Circundante al Glaciar/Lago</b>: Pendientes pronunciadas son fuentes potenciales de avalanchas de roca</li>
            <li><b>Geología del Terreno Circundante</b>: Influye en la estabilidad de las laderas</li>
            <li><b>Presencia de Inestabilidades Previas</b>: Cicatrices de deslizamientos antiguos</li>
          </ul>
        </li>
        <li><b>D.2:</b> Desde el Glaciar
          <ul>
            <li><b>Presencia de Grietas (Crevasses)</b>: Enfatizando su rol en desprendimientos</li>
          </ul>
        </li>
      </ul>
    </li>
    <li><b>E:</b> Características del Lago Glaciar
      <ul>
        <li><b>E.1:</b> Represa del Lago
          <ul>
            <li><b>Tipo de Represa del Lago</b>: Morrena, hielo, roca (morrena e hielo tienen mayor riesgo)</li>
            <li><b>Geometría de la Represa</b>: Ancho de la cresta, pendiente, longitud</li>
            <li><b>Material de la Represa</b>: Cohesión, permeabilidad (para represas de morrena)</li>
          </ul>
        </li>
        <li><b>E.2:</b> Geometría del Lago
          <ul>
            <li><b>Área del Lago Glaciar</b>: Mayor área implica mayor volumen potencial de desbordamiento</li>
            <li><b>Volumen del Lago Glaciar</b>: Directamente relacionado con la magnitud potencial de la inundación</li>
            <li><b>Profundidad del Lago</b>: Influye en la estabilidad y la respuesta a impactos</li>
            <li><b>Nivel de Borde Libre (Freeboard)</b>: Menor borde libre aumenta el riesgo de desbordamiento</li>
          </ul>
        </li>
      </ul>
    </li>
    <li><b>F:</b> Factores Ambientales y de Contexto
      <ul>
        <li><b>F.1:</b> Clima
          <ul>
            <li><b>Temperatura</b>: Aumento acelera la fusión y la inestabilidad</li>
            <li><b>Precipitación (Nieve y Lluvia)</b>: Lluvias intensas pueden contribuir a la fusión y desencadenar flujos de escombros</li>
            <li><b>Eventos Climáticos Extremos</b>: Olas de calor, tormentas intensas</li>
          </ul>
        </li>
        <li><b>F.2:</b> Geodinámica
          <ul>
            <li><b>Actividad Sísmica</b>: Terremotos pueden desencadenar inestabilidad</li>
            <li><b>Actividad Tectónica Regional</b>: Fallas activas cercanas</li>
          </ul>
        </li>
        <li><b>F.3:</b> Cambios en el Tiempo
          <ul>
            <li><b>Tasa de Crecimiento del Lago</b>: Rápida expansión indica mayor peligrosidad</li>
            <li><b>Cambios en la Masa del Glaciar Padre</b>: Pérdida de masa puede aumentar la probabilidad de formación de lagos</li>
          </ul>
        </li>
      </ul>
    </li>
    <li><b>G:</b> Susceptibilidad del Terreno Aguas Abajo
      <ul>
        <li><b>G.1:</b> Impacto Potencial
          <ul>
            <li><b>Pendiente del Valle Aguas Abajo</b>: Influye en la velocidad y alcance potencial de una inundación</li>
            <li><b>Presencia de Constricciones o Embalsamientos Naturales</b>: Pueden modificar el flujo de la inundación</li>
            <li><b>Tipo de Suelo y Cobertura Vegetal</b>: Impacta la absorción y propagación del agua</li>
          </ul>
        </li>
      </ul>
    </li>
  </ul>
</div>

<script>
function toggleTaxonomia() {
    var panel = document.getElementById('taxonomiaPanel');
    if (panel.style.display === 'none') {
        panel.style.display = 'block';
    } else {
        panel.style.display = 'none';
    }
}
</script>
"""

m.get_root().html.add_child(Element(taxonomia_html))

# Mostrar el mapa
m.save("mapa_interactivo.html")
