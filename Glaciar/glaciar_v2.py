import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="Evaluación de Glaciares")

# Estilo CSS para la app
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #f0f4f8;
        color: #333;
    }

    .stButton>button {
        background-color: #0066cc;
        color: white;
        border-radius: 8px;
        height: 42px;
        font-size: 15px;
        font-weight: 600;
        border: none;
        transition: 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #004999;
    }

    .stSidebar {
        background-color: #eaf1f8;
    }

    .stSelectbox, .stFileUploader, .stTextInput, .stMultiselect {
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #d6d6d6;
        padding: 8px;
    }

    .stDataFrame {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #d6d6d6;
        padding: 16px;
        box-shadow: 1px 1px 6px rgba(0, 0, 0, 0.05);
    }

    .stMarkdown {
        font-size: 15px;
        color: #444;
    }

    h1, h2, h3 {
        color: #005a9e;
    }

    /* Caja de taxonomía flotante mejorada */
    .taxonomia-box {
        position: fixed;
        top: 80px;
        right: 30px;
        width: 420px;
        max-height: 500px;
        overflow-y: auto;
        background-color: white;
        border: 1px solid #ccc;
        padding: 18px;
        z-index: 1000;
        font-size: 14px;
        box-shadow: 4px 4px 20px rgba(0,0,0,0.2);
        border-radius: 10px;
    }

    .taxonomia-box h2 {
        font-size: 18px;
        color: #005a9e;
        margin-bottom: 10px;
    }

    .taxonomia-box ul {
        padding-left: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Título de la app
st.title("🧊 Evaluación de Glaciares con PROMETHEE II")

# ========== FUNCIONES DE MAPA ==========

def agregar_taxonomia():
    # HTML de la taxonomía
    taxonomia_html = """
    <div class="taxonomia-box">
      <h2>Taxonomía de Evaluación de Glaciares</h2>
      <ul>
        <li><b>A:</b> Características del Glaciar Padre
          <ul>
            <li><b>A.1:</b> Geometría del Glaciar
              <ul>
                <li><b>A.1.a:</b> Tamaño
                  <ul>
                    <li><b>Área del Glaciar Padre:</b> Un área mayor puede implicar un mayor volumen de hielo</li>
                    <li><b>Volumen del Glaciar:</b> Inferido de 'Área' y 'Espesor'</li>
                    <li><b>Longitud del Glaciar:</b> Considerado en la selección de lagos potencialmente peligrosos</li>
                    <li><b>Ancho del Glaciar:</b> Considerado en la selección de lagos potencialmente peligrosos</li>
                  </ul>
                </li>
                <li><b>A.1.b:</b> Morfología y Pendiente
                  <ul>
                    <li><b>Pendiente de la Lengua del Glaciar:</b> Una pendiente pronunciada puede aumentar la probabilidad de avalanchas de hielo</li>
                    <li><b>Presencia de Grietas (Crevasses):</b> Pueden indicar inestabilidad y ser puntos de desprendimiento de avalanchas</li>
                  </ul>
                </li>
              </ul>
            </li>
            <li><b>A.2:</b> Ubicación y Elevación
              <ul>
                <li><b>Elevación del Glaciar Madre:</b> Influye en las condiciones climáticas y la tasa de fusión del hielo</li>
                <li><b>Orientación del Glaciar (Aspecto):</b> Puede influir en la radiación solar recibida y la tasa de fusión</li>
              </ul>
            </li>
            <li><b>A.3:</b> Subsuelo Glaciar
              <ul>
                <li><b>Topografía Subglacial (Bed Topography):</b> La presencia de sobre-profundizaciones crea sitios favorables para la formación de lagos</li>
                <li><b>Espesor del Hielo:</b> Crucial para estimar la topografía subglacial y la posibilidad de formación de depresiones</li>
              </ul>
            </li>
          </ul>
        </li>
        <li><b>B:</b> Dinámica y Comportamiento Glaciar
          <ul>
            <li><b>B.1:</b> Estado y Cambios del Glaciar
              <ul>
                <li><b>Retroceso Glaciar:</b> Lleva a la formación y expansión de lagos proglaciales</li>
                <li><b>Avance Glaciar (Surge):</b> Puede bloquear el drenaje y formar lagos represados por hielo</li>
                <li><b>Tasa de Expansión/Retroceso:</b> Indica la rapidez de los cambios y el potencial de formación o crecimiento de lagos</li>
              </ul>
            </li>
            <li><b>B.2:</b> Procesos Activos
              <ul>
                <li><b>Actividad de Avalanchas de Hielo:</b> Pueden alcanzar lagos y desencadenar GLOFs</li>
                <li><b>Velocidad de Flujo del Glaciar:</b> Velocidades extremas pueden indicar inestabilidad</li>
                <li><b>Fusión del Hielo (Snow/Ice Melt Water):</b> El aumento puede incrementar el nivel de los lagos y la presión sobre las represas</li>
              </ul>
            </li>
          </ul>
        </li>
        <li><b>C:</b> Interacción Glaciar - Lago Glaciar
          <ul>
            <li><b>C.1:</b> Proximidad
              <ul>
                <li><b>Distancia entre el Término del Glaciar y el Lago:</b> Menor distancia aumenta la probabilidad de impacto</li>
                <li><b>Contacto Glaciar-Lago:</b> El contacto directo aumenta la susceptibilidad a GLOFs</li>
              </ul>
            </li>
            <li><b>C.2:</b> Conexión
              <ul>
                <li><b>Conexión Hidrológica:</b> La existencia de conexión directa influye en la dinámica del lago</li>
                <li><b>Tipo de Lago Glaciar:</b> Proglacial (conectado), desconectado, supraglaciar</li>
              </ul>
            </li>
          </ul>
        </li>
      </ul>
    </div>
    """
    return taxonomia_html


# ========== FUNCIONES MCDA ==========
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
            score = sum(
                weights[j] * preference_function_type_v(data[i, j] - data[k, j], q_vals[j], p_vals[j])
                for j in range(m)
            )
            preference_matrix[i, k] = score
    return preference_matrix

def compute_flows(matrix):
    n = matrix.shape[0]
    phi_plus = np.sum(matrix, axis=1) / (n - 1)
    phi_minus = np.sum(matrix, axis=0) / (n - 1)
    phi = phi_plus - phi_minus
    return phi_plus, phi_minus, phi

def color_por_riesgo(score):
    if score < 0:
        return 'red'
    elif score < 0.29:
        return 'orange'
    else:
        return 'green'

# ========== LAYOUT ==========
# Sidebar con filtros y selector de archivo
st.sidebar.title("Configuración de Mapa")
archivo = st.sidebar.file_uploader("📁 Sube un archivo CSV con los datos de glaciares", type="csv")

# Filtros de color
riesgo_filtro = st.sidebar.multiselect(
    "Filtrar por nivel de riesgo",
    options=['red', 'orange', 'green'],
    default=['red', 'orange', 'green']
)

# Mapa base
map_center = [-33.6, -70.2]
m = folium.Map(location=map_center, zoom_start=9)

# Manejo del estado de la visibilidad de la taxonomía con st.session_state
if 'mostrar_taxonomia' not in st.session_state:
    st.session_state.mostrar_taxonomia = False

# Botón para mostrar/ocultar taxonomía
if st.sidebar.button("Mostrar/Ocultar Taxonomía"):
    st.session_state.mostrar_taxonomia = not st.session_state.mostrar_taxonomia

# Agregar la taxonomía al mapa según el estado del botón
taxonomia_html = agregar_taxonomia() if st.session_state.mostrar_taxonomia else ""
st.markdown(taxonomia_html, unsafe_allow_html=True)

# ========== PANEL DE PROCESAMIENTO DE DATOS ==========
if archivo:
    df = pd.read_csv(archivo, sep=';', encoding='ISO-8859-1')
    df.columns = df.columns.str.strip().str.lower()

    for col in df.columns:
        if col not in ['lat', 'lon', 'nombre_glaciar']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['lon'], df['lat']),
        crs="EPSG:4326"
    )

    criterios = [col for col in df.columns if col not in ['lat', 'lon', 'nombre_glaciar']]
    data = gdf[criterios].to_numpy()

    pesos = np.full(len(criterios), 1 / len(criterios))
    q_vals = np.full(len(criterios), 0.5)
    p_vals = np.full(len(criterios), 5.0)

    pref_matrix = compute_preference_matrix(data, pesos, q_vals, p_vals)
    phi_plus, phi_minus, phi = compute_flows(pref_matrix)

    gdf['phi_plus'] = phi_plus
    gdf['phi_minus'] = phi_minus
    gdf['riesgo'] = phi

    # Estado para mostrar/ocultar la tabla de resultados
    if 'mostrar_tabla' not in st.session_state:
        st.session_state.mostrar_tabla = False  # Oculto por defecto

    if st.sidebar.button("Mostrar/Ocultar Ranking de Glaciares"):
        st.session_state.mostrar_tabla = not st.session_state.mostrar_tabla

    if st.session_state.mostrar_tabla:
        st.subheader("📊 Ranking de Glaciares")
        ranking = pd.DataFrame({
            'Glaciar': gdf['nombre_glaciar'],
            'Φ⁺': phi_plus,
            'Φ⁻': phi_minus,
            'Φ (Neto)': phi
        }).sort_values(by='Φ (Neto)', ascending=False)
        st.dataframe(ranking)

    # Filtrar por color
    colores_permitidos = riesgo_filtro
    gdf_filtrado = gdf[gdf['riesgo'].apply(color_por_riesgo).isin(colores_permitidos)]

    # Agregar puntos al mapa
    for _, fila in gdf_filtrado.iterrows():
        lat, lon = fila.geometry.y, fila.geometry.x
        color = color_por_riesgo(fila['riesgo'])

        folium.Circle(
            location=[lat, lon],
            radius=1500,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            popup=folium.Popup(
                f"<b>{fila['nombre_glaciar']}</b><br>Φ: {fila['riesgo']:.3f}<br>Φ⁺: {fila['phi_plus']:.3f}<br>Φ⁻: {fila['phi_minus']:.3f}",
                max_width=300
            )
        ).add_to(m)

# Mostrar mapa con o sin puntos
st.subheader("🗺️ Mapa Interactivo")
st_data = st_folium(m, width=1200, height=600)