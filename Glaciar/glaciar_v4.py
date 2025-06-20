import joblib
import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import folium
import yaml
from streamlit_folium import st_folium
from prometheeII import promethee_matrix, color_por_riesgo
from todim import todim_matrix
from sklearn.preprocessing import StandardScaler

st.set_page_config(layout="wide", page_title="Evaluación de Glaciares")

# ========= Estilo CSS con background atractivo =========
st.markdown("""
<style>
body {
    background-image: url('https://images.unsplash.com/photo-1587049352854-9d18ddce3c1a');
    background-size: cover;
    background-attachment: fixed;
}

.main {
    background-color: rgba(255, 255, 255, 0.85);
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.navbar {
    background-color: #2c3e50;
    padding: 12px;
    color: white;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    border-bottom: 4px solid #2980b9;
    margin-bottom: 20px;
    border-radius: 0 0 10px 10px;
}

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

st.markdown('<div class="navbar">🧊 GlacIA-R : Evaluación de Riesgo de Glaciares</div>', unsafe_allow_html=True)


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

metodo = st.sidebar.selectbox(
    "🧮 Selecciona el método de evaluación",
    options=["PROMETHEE", "TODIM", "Red Neuronal"]
)

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

    # Pesos de los criterios
    pesos = np.full(len(criterios), 1 / len(criterios))

    # Parametros PROMETHEE
    if metodo == "PROMETHEE":
        st.sidebar.markdown("### Parámetros de PROMETHEE")
        q_valor = st.sidebar.slider("q (umbral de indiferencia)", 0.0, 5.0, 0.5, 0.1)
        p_valor = st.sidebar.slider("p (umbral de preferencia)", 0.0, 10.0, 5.0, 0.5)
        q_vals = np.full(len(criterios), q_valor)
        p_vals = np.full(len(criterios), p_valor)
    # q_vals = np.full(len(criterios), 0.5)
    # p_vals = np.full(len(criterios), 5.0)

    # Parametros TODIM
    if metodo == "TODIM":
        st.sidebar.markdown("### Parámetros de TODIM")
        alpha = st.sidebar.slider("α (ganancia)", 0.1, 3.0, 1.0, 0.1)
        beta = st.sidebar.slider("β (pérdida)", 0.1, 3.0, 1.0, 0.1)
        lambd = st.sidebar.slider("λ (atenuación de pérdidas)", 0.1, 3.0, 1.0, 0.1)

    #  METODO MCDA
    if metodo == "PROMETHEE":
        ranking = promethee_matrix(data, pesos, q_vals, p_vals)
    elif metodo == "TODIM":
        ranking = todim_matrix(data, pesos, alpha=alpha, beta=beta, lambd=lambd)
    elif metodo == "Red Neuronal":
        try:
            model = joblib.load("modelo_phi_mlp.pkl")
            scaler = model['scaler']
            mlp = model['mlp']
            data_df = pd.DataFrame(data, columns=criterios)
            data_scaled = scaler.transform(data_df)
            ranking = mlp.predict(data_scaled)
        except Exception as e:
            st.error(f"Error al cargar el modelo de red neuronal: {e}")
            st.stop()
    else:
        st.error("Método de evaluación no soportado.")
        st.stop()

    # phi = promethee_matrix(data, pesos, q_vals, p_vals)
    gdf['riesgo'] = ranking

    # if st.session_state.mostrar_tabla:
    #     st.subheader("📊 Ranking de Glaciares")
    #     ranking = pd.DataFrame({
    #         'Glaciar': gdf['nombre_glaciar'],
    #         'Ranking': ranking
    #     }).sort_values(by='Ranking', ascending=False)
    #     st.dataframe(ranking)

    # if st.session_state.mostrar_tabla:
    #     st.subheader("📊 Ranking de Glaciares (Normalizado)")
    #
    #     # Normalizar rankings al intervalo [0, 1]
    #     ranking_array = np.array(ranking)
    #     ranking_norm = (ranking_array - np.min(ranking_array)) / (np.max(ranking_array) - np.min(ranking_array))
    #
    #     # Agregar al GeoDataFrame
    #     gdf['ranking_normalizado'] = ranking_norm
    #
    #     # Crear tabla
    #     tabla = pd.DataFrame({
    #         'Fila': gdf.index,
    #         'Glaciar': gdf['nombre_glaciar'],
    #         'Ranking Normalizado': ranking_norm
    #     }).sort_values(by='Ranking Normalizado', ascending=False)
    #
    #     st.dataframe(tabla)
    #
    #     # Gráfico de barras
    #     st.subheader("📈 Gráfico de Barras del Ranking Normalizado")
    #     st.bar_chart(pd.DataFrame({
    #         'Ranking Normalizado': ranking_norm
    #     }, index=gdf.index))

    import plotly.express as px

    if st.session_state.mostrar_tabla:
        st.markdown("## 📊 Ranking de Glaciares (Normalizado)", unsafe_allow_html=True)

        # Normalizar rankings al intervalo [0, 1]
        ranking_array = np.array(ranking)
        ranking_norm = (ranking_array - np.min(ranking_array)) / (np.max(ranking_array) - np.min(ranking_array))
        gdf['ranking_normalizado'] = ranking_norm

        # Crear DataFrame ordenado
        tabla = pd.DataFrame({
            'Fila': gdf.index,
            'Glaciar': gdf['nombre_glaciar'],
            'Ranking Normalizado': np.round(ranking_norm, 3)
        }).sort_values(by='Ranking Normalizado', ascending=False).reset_index(drop=True)

        # Mostrar tabla con estilo
        st.dataframe(tabla.style
                     .background_gradient(cmap='Blues', subset=['Ranking Normalizado'])
                     .format({'Ranking Normalizado': '{:.3f}'})
                     .set_properties(**{
            'text-align': 'center',
            'font-family': 'Arial',
            'font-size': '14px'
        }), height=400, use_container_width=True)

        # Gráfico de barras con Plotly
        st.markdown("## 📈 Gráfico de Barras del Ranking Normalizado", unsafe_allow_html=True)
        fig = px.bar(
            tabla,
            x='Fila',
            y='Ranking Normalizado',
            color='Ranking Normalizado',
            color_continuous_scale='Blues',
            labels={'Ranking Normalizado': 'Ranking'},
            height=400
        )
        fig.update_layout(
            xaxis_title="Fila del Glaciar",
            yaxis_title="Ranking Normalizado",
            template="plotly_white",
            margin=dict(t=10, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

    gdf_filtrado = gdf[gdf['riesgo'].apply(color_por_riesgo).isin(riesgo_filtro)]

    for _, fila in gdf_filtrado.iterrows():
        lat, lon = fila.geometry.y, fila.geometry.x
        color = color_por_riesgo(fila['riesgo'])

        popup_text = f"<b>{fila['nombre_glaciar']}</b><br>ranking: {fila['riesgo']:.3f}"
        if metodo == "PROMETHEE":
            # Solo agregar si existen las columnas en el DataFrame
            if 'phi_plus' in fila and 'phi_minus' in fila:
                popup_text += f"<br>Φ⁺: {fila['phi_plus']:.3f}<br>Φ⁻: {fila['phi_minus']:.3f}"

        folium.Circle(
            location=[lat, lon],
            radius=1500,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)

# ========= Mostrar mapa =========
st.subheader("🗺️ Mapa Interactivo")
st_data = st_folium(m, width=1200, height=600)

# ========= Mostrar taxonomía =========
if st.session_state.mostrar_taxonomia:
    st.markdown(cargar_taxonomia_desde_yaml(), unsafe_allow_html=True)
