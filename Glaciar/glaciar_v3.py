import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import folium
import yaml
from streamlit_folium import st_folium
from prometheeII import promethee_matrix, color_por_riesgo

st.set_page_config(layout="wide", page_title="Evaluación de Glaciares")

# ========= Estilo CSS para dashboard y panel lateral =========
st.markdown("""
<style>
/* Barra de navegación superior */
.navbar {
    background-color: #2c3e50;
    padding: 12px;
    color: white;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    border-bottom: 4px solid #2980b9;
    margin-bottom: 20px;
}

/* Botón de barra de navegación */
.stButton > button {
    background-color: #2980b9;
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    border: none;
}
.stButton > button:hover {
    background-color: #3498db;
}

/* Panel lateral derecho */
.taxonomia-panel {
    position: fixed;
    top: 100px;
    right: 20px;
    width: 400px;
    max-height: 80%;
    overflow-y: auto;
    background-color: white;
    border: 2px solid #888;
    padding: 16px;
    z-index: 9999;
    font-size: 13px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
    border-radius: 6px;
}
.taxonomia-panel h2 {
    font-size: 18px;
    margin-bottom: 10px;
    color: #2c3e50;
}
.taxonomia-panel ul {
    padding-left: 20px;
}
</style>
""", unsafe_allow_html=True)

# ========= Barra de navegación tipo dashboard =========
st.markdown('<div class="navbar">🧊 Evaluación de Glaciares con PROMETHEE II</div>', unsafe_allow_html=True)

# ========= Función para cargar y renderizar taxonomía desde YAML =========
def cargar_taxonomia_desde_dict(data):
    def recorrer_nodos(nodo):
        html = "<ul>"
        if isinstance(nodo, dict):
            for clave, valor in nodo.items():
                html += "<li>"
                if isinstance(valor, dict):
                    nombre = valor.get("nombre", "")
                    descripcion = valor.get("descripcion", "")
                    if nombre or descripcion:
                        html += f"<b>{clave}:</b> {nombre}"
                        if descripcion:
                            html += f"<br><i>{descripcion}</i>"
                        # Recursión para subnodos
                        subnodos = {k: v for k, v in valor.items() if isinstance(v, dict) or isinstance(v, list)}
                        if subnodos:
                            html += recorrer_nodos(subnodos)
                    else:
                        html += f"<b>{clave}</b>"
                        html += recorrer_nodos(valor)
                elif isinstance(valor, list):
                    html += f"<b>{clave}</b><ul>"
                    for item in valor:
                        if isinstance(item, dict):
                            nombre = item.get("nombre", "")
                            descripcion = item.get("descripcion", "")
                            html += "<li>"
                            if nombre:
                                html += f"<b>{nombre}</b>"
                            if descripcion:
                                html += f"<br><i>{descripcion}</i>"
                            html += "</li>"
                        else:
                            html += f"<li>{item}</li>"
                    html += "</ul>"
                else:
                    html += f"<b>{clave}:</b> {valor}"
                html += "</li>"
        html += "</ul>"
        return html

    return f"""<div class="taxonomia-panel"><h2>📖 Taxonomía de Evaluación</h2>{recorrer_nodos(data)}</div>"""


def cargar_taxonomia_desde_yaml(path="taxonomia_glaciares_completa.yaml"):
    with open(path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return cargar_taxonomia_desde_dict(data)



# ========= Estado =========
if 'mostrar_taxonomia' not in st.session_state:
    st.session_state.mostrar_taxonomia = False
if 'mostrar_tabla' not in st.session_state:
    st.session_state.mostrar_tabla = False

# ========= Sidebar =========
st.sidebar.title("Menú de Configuración")
archivo = st.sidebar.file_uploader("📁 Subir archivo CSV de glaciares", type="csv")

riesgo_filtro = st.sidebar.multiselect(
    "🎯 Filtrar por nivel de riesgo",
    options=['red', 'orange', 'green'],
    default=['red', 'orange', 'green']
)

if st.sidebar.button("🔍 Mostrar/Ocultar Taxonomía"):
    st.session_state.mostrar_taxonomia = not st.session_state.mostrar_taxonomia

if st.sidebar.button("📊 Mostrar/Ocultar Ranking"):
    st.session_state.mostrar_tabla = not st.session_state.mostrar_tabla

# ========= Mapa base =========
map_center = [-33.6, -70.2]
m = folium.Map(location=map_center, zoom_start=8)

# ========= Cargar y procesar datos =========
if archivo:
    df = pd.read_csv(archivo, sep=';', encoding='ISO-8859-1')
    df.columns = df.columns.str.strip().str.lower()

    for col in df.columns:
        if col not in ['lat', 'lon', 'nombre_glaciar']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['lon'], df['lat']), crs="EPSG:4326")
    criterios = [col for col in df.columns if col not in ['lat', 'lon', 'nombre_glaciar']]
    data = gdf[criterios].to_numpy()

    # Parametros PROMETHEE
    pesos = np.full(len(criterios), 1 / len(criterios))
    q_vals = np.full(len(criterios), 0.5)
    p_vals = np.full(len(criterios), 5.0)

    #  METODO PROMETHEE
    phi = promethee_matrix(data, pesos, q_vals, p_vals)
    gdf['riesgo'] = phi

    if st.session_state.mostrar_tabla:
        st.subheader("📊 Ranking de Glaciares")
        ranking = pd.DataFrame({
            'Glaciar': gdf['nombre_glaciar'],
            'Φ (Neto)': phi
        }).sort_values(by='Φ (Neto)', ascending=False)
        st.dataframe(ranking)

    gdf_filtrado = gdf[gdf['riesgo'].apply(color_por_riesgo).isin(riesgo_filtro)]

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

# ========= Mostrar mapa =========
st.subheader("🗺️ Mapa Interactivo")
st_data = st_folium(m, width=1200, height=600)

# ========= Mostrar taxonomía =========
if st.session_state.mostrar_taxonomia:
    st.markdown(cargar_taxonomia_desde_yaml(), unsafe_allow_html=True)
