import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
import joblib
# librería para IA
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import streamlit as st


# # Cargar el archivo CSV especificando que el delimitador es punto y coma (;)
# df = pd.read_csv('ranking_promethee.csv', sep=';')
#
# # Limpiar los nombres de las columnas
# df.columns = df.columns.str.strip()
#
# # Verificar las columnas después de limpiarlas
# print("Columnas después de limpiar espacios:", df.columns)
#
# # Selección de las columnas relevantes para las características
# X = df[['pendiente', 'volumen', 'proximidad_lago', 'ancho']]  # Características
# y = df['ranking'].values  # El ranking como objetivo
#
# # Verificar el contenido de X y y
# print("Datos de entrada (X):")
# print(X.head())  # Muestra las primeras filas de las características
# print("Datos de salida (y):")
# print(y[:5])  # Muestra las primeras 5 filas de los rankings
# # Escalamiento de las características
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)  # Escalar las características
#
# # Verificar que X_scaled tenga la forma correcta
# print("Datos escalados (X_scaled):")
# print(X_scaled[:5])  # Muestra las primeras 5 filas escaladas
#
# # Crear y entrenar el modelo de red neuronal
# mlp = MLPRegressor(hidden_layer_sizes=(50, 50), max_iter=1000, random_state=42)
# mlp.fit(X_scaled, y)
#
# # Guardar el modelo y el escalador
# # joblib.dump({'scaler': scaler, 'mlp': mlp}, 'modelo_phi_mlp.pkl')
# joblib.dump((mlp, scaler), 'modelo_phi_mlp.pkl')
#
# print("Modelo entrenado y guardado como 'modelo_phi_mlp.pkl'")


# ======= MODULOS PARA IA =========================
def guardar_evaluacion_para_entrenamiento(df_glaciares, ranking, archivo):
    df_train = df_glaciares.copy()
    df_train["phi"] = ranking
    try:
        df_existente = pd.read_csv(archivo)
        df_combinado = pd.concat([df_existente, df_train], ignore_index=True)
    except FileNotFoundError:
        df_combinado = df_train
    df_combinado.to_csv(archivo, index=False)


def reentrenar_red_neuronal(df, modelo_guardado):

    X = df.drop(columns=['phi', 'nombre_glaciar', 'lat', 'lon'])
    y = df['phi']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = MLPRegressor(hidden_layer_sizes=(50, 30), max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)

    joblib.dump((model, scaler), modelo_guardado)
    st.success("✅ Red neuronal reentrenada y guardada correctamente.")


def predecir_con_red_neuronal(data, criterios, modelo_path):
    if not os.path.exists(modelo_path):
        st.error("Modelo no entrenado aún.")
        return None

    data_df = pd.DataFrame(data, columns=criterios)
    model, scaler = joblib.load("modelo_phi_mlp.pkl")
    data_scaled = scaler.transform(data_df)
    ranking = model.predict(data_scaled)

    return ranking


# ======== FIN MODULOS IA =======================
