# modulo_grafico_barras.py

import plotly.express as px
import streamlit as st


def mostrar_grafico_comparativo(comparacion_df, fontsize_title, fontsize_ticks, fontsize_labels, height_comp, width_comp):
    """
    Muestra un gráfico de barras comparativo para rankings de glaciares.

    Parámetros:
    - df_comparativo: DataFrame con columnas = métodos, índice = glaciares.
    - figsize: tamaño de la figura.
    - fontsize_labels: tamaño de fuente de etiquetas.
    - titulo: título opcional para mostrar sobre el gráfico.
    """

    st.markdown("## Comparación de rankings entre métodos", unsafe_allow_html=True)

    # # Datos base
    # df_scatter = df_heatmap.copy()
    # df_scatter['Glaciar'] = gdf['nombre_glaciar'].values
    #
    # # Lista de métodos a comparar
    # metodos = ['PROMETHEE', 'TODIM', 'MAVT', 'Red Neuronal']
    # n = len(metodos)

    fig_comparacion = px.bar(
        comparacion_df,
        x='Glaciar',
        y=['PROMETHEE', 'TODIM', 'MAVT', 'Red Neuronal'],
        title= "",
        labels={"value": "Ranking Normalizado", "variable": "Método"},
        barmode='group'
    )
    fig_comparacion.update_layout(
        # title_font=dict(size=fontsize_title),  # Tamaño del título
        xaxis_title="Glaciar",
        yaxis_title="Ranking Normalizado",
        xaxis_tickangle=-45,
        xaxis=dict(
            tickfont=dict(size=fontsize_ticks),  # Tamaño de etiquetas del eje X
            title_font=dict(size=fontsize_labels)  # Tamaño del título del eje X
        ),
        yaxis=dict(
            tickfont=dict(size=fontsize_ticks),  # Tamaño de etiquetas del eje Y
            title_font=dict(size=fontsize_labels)  # Tamaño del título del eje Y
        ),
        legend=dict(font=dict(size=fontsize_labels)),  # Tamaño de fuente de leyenda
        height=height_comp,
        width=width_comp,
        margin=dict(t=50, b=150, l=50, r=50),
        template="plotly_white"
    )
    st.plotly_chart(fig_comparacion, use_container_width=True, key="comparacion_general")