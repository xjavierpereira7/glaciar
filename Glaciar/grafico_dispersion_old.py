# modulo_grafico_dispersion.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def mostrar_grafico_dispersion(df_scatter, fontsize_title, fontsize_labels, height_disp, width_disp):
    """
    Muestra gráficos de dispersión pareados para comparar métodos.

    Parámetros:
    - df_comparativo: DataFrame con columnas = métodos, índice = glaciares.
    - figsize: tamaño de la figura.
    - fontsize_labels: tamaño de fuente para etiquetas.
    - titulo: título del gráfico.
    """



    # Matriz de dispersión entre métodos
    st.markdown("## 🌫️ Dispersión de rankings entre métodos", unsafe_allow_html=True)

    metodos = ['PROMETHEE', 'TODIM', 'MAVT', 'Red Neuronal']
    n = len(metodos)

    fig = make_subplots(rows=n, cols=n, shared_xaxes=True, shared_yaxes=True,
                        horizontal_spacing=0.02, vertical_spacing=0.02)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue

            x = df_scatter[metodos[j]]
            y = df_scatter[metodos[i]]

            # Mancha de densidad
            fig.add_trace(go.Histogram2dContour(
                x=x,
                y=y,
                colorscale='Blues',
                contours=dict(coloring='heatmap'),
                showscale=False,
                ncontours=15,
                opacity=0.6
            ), row=i + 1, col=j + 1)

            # Puntos encima
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='markers',
                marker=dict(size=4, color='black', opacity=0.5),
                showlegend=False
            ), row=i + 1, col=j + 1)

            # Línea de identidad
            min_val = min(x.min(), y.min())
            max_val = max(x.max(), y.max())
            fig.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                line=dict(color='gray', dash='dot'),
                showlegend=False
            ), row=i + 1, col=j + 1)

            # Etiquetas de ejes
            if i == n - 1:
                fig.update_xaxes(title_text=metodos[j], row=i + 1, col=j + 1)
            if j == 0:
                fig.update_yaxes(title_text=metodos[i], row=i + 1, col=j + 1)

    fig.update_layout(height=height_disp * n,
                      width=width_disp * n,
                      font=dict(size=fontsize_labels),
                      margin=dict(t=50, l=50, r=20, b=20))

    # ✅ Agrega un key único
    st.plotly_chart(fig, use_container_width=True, key="grafico_dispersion_manchas")