import yaml

taxonomia_glaciares = {
    "A": {
        "nombre": "Características del Glaciar Padre",
        "A.1": {
            "nombre": "Geometría del Glaciar",
            "A.1.a": {
                "nombre": "Tamaño",
                "criterios": [
                    {"nombre": "Área del Glaciar Padre", "descripcion": "Un área mayor puede implicar un mayor volumen de hielo"},
                    {"nombre": "Volumen del Glaciar", "descripcion": "Inferido de 'Área' y 'Espesor'"},
                    {"nombre": "Longitud del Glaciar", "descripcion": "Considerado en la selección de lagos potencialmente peligrosos"},
                    {"nombre": "Ancho del Glaciar", "descripcion": "Considerado en la selección de lagos potencialmente peligrosos"}
                ]
            },
            "A.1.b": {
                "nombre": "Morfología y Pendiente",
                "criterios": [
                    {"nombre": "Pendiente de la Lengua del Glaciar", "descripcion": "Una pendiente pronunciada puede aumentar la probabilidad de avalanchas de hielo"},
                    {"nombre": "Presencia de Grietas (Crevasses)", "descripcion": "Pueden indicar inestabilidad y ser puntos de desprendimiento de avalanchas"}
                ]
            }
        },
        "A.2": {
            "nombre": "Ubicación y Elevación",
            "criterios": [
                {"nombre": "Elevación del Glaciar Madre", "descripcion": "Influye en las condiciones climáticas y la tasa de fusión del hielo"},
                {"nombre": "Orientación del Glaciar (Aspecto)", "descripcion": "Puede influir en la radiación solar recibida y la tasa de fusión"}
            ]
        },
        "A.3": {
            "nombre": "Subsuelo Glaciar",
            "criterios": [
                {"nombre": "Topografía Subglacial (Bed Topography)", "descripcion": "La presencia de sobre-profundizaciones crea sitios favorables para la formación de lagos"},
                {"nombre": "Espesor del Hielo", "descripcion": "Crucial para estimar la topografía subglacial y la posibilidad de formación de depresiones"}
            ]
        }
    },
    "B": {
        "nombre": "Dinámica y Comportamiento Glaciar",
        "B.1": {
            "nombre": "Estado y Cambios del Glaciar",
            "criterios": [
                {"nombre": "Retroceso Glaciar", "descripcion": "Lleva a la formación y expansión de lagos proglaciales"},
                {"nombre": "Avance Glaciar (Surge)", "descripcion": "Puede bloquear el drenaje y formar lagos represados por hielo"},
                {"nombre": "Tasa de Expansión/Retroceso", "descripcion": "Indica la rapidez de los cambios y el potencial de formación o crecimiento de lagos"}
            ]
        },
        "B.2": {
            "nombre": "Procesos Activos",
            "criterios": [
                {"nombre": "Actividad de Avalanchas de Hielo", "descripcion": "Pueden alcanzar lagos y desencadenar GLOFs"},
                {"nombre": "Velocidad de Flujo del Glaciar", "descripcion": "Velocidades extremas pueden indicar inestabilidad"},
                {"nombre": "Fusión del Hielo (Snow/Ice Melt Water)", "descripcion": "El aumento puede incrementar el nivel de los lagos y la presión sobre las represas"}
            ]
        }
    },
    "C": {
        "nombre": "Interacción Glaciar - Lago Glaciar",
        "C.1": {
            "nombre": "Proximidad",
            "criterios": [
                {"nombre": "Distancia entre el Término del Glaciar y el Lago", "descripcion": "Menor distancia aumenta la probabilidad de impacto"},
                {"nombre": "Contacto Glaciar-Lago", "descripcion": "El contacto directo aumenta la susceptibilidad a GLOFs"}
            ]
        },
        "C.2": {
            "nombre": "Conexión",
            "criterios": [
                {"nombre": "Conexión Hidrológica", "descripcion": "La existencia de conexión directa influye en la dinámica del lago"},
                {"nombre": "Tipo de Lago Glaciar", "descripcion": "Proglacial (conectado), desconectado, supraglaciar"}
            ]
        }
    },
    "D": {
        "nombre": "Susceptibilidad a Desprendimientos de Masa",
        "D.1": {
            "nombre": "Terreno Adyacente",
            "criterios": [
                {"nombre": "Pendiente del Terreno Circundante al Glaciar/Lago", "descripcion": "Pendientes pronunciadas son fuentes potenciales de avalanchas de roca"},
                {"nombre": "Geología del Terreno Circundante", "descripcion": "Influye en la estabilidad de las laderas"},
                {"nombre": "Presencia de Inestabilidades Previas", "descripcion": "Cicatrices de deslizamientos antiguos"}
            ]
        },
        "D.2": {
            "nombre": "Desde el Glaciar",
            "criterios": [
                {"nombre": "Presencia de Grietas (Crevasses)", "descripcion": "Enfatizando su rol en desprendimientos"}
            ]
        }
    },
    "E": {
        "nombre": "Características del Lago Glaciar",
        "E.1": {
            "nombre": "Represa del Lago",
            "criterios": [
                {"nombre": "Tipo de Represa del Lago", "descripcion": "Morrena, hielo, roca (morrena e hielo tienen mayor riesgo)"},
                {"nombre": "Geometría de la Represa", "descripcion": "Ancho de la cresta, pendiente, longitud"},
                {"nombre": "Material de la Represa", "descripcion": "Cohesión, permeabilidad (para represas de morrena)"}
            ]
        },
        "E.2": {
            "nombre": "Geometría del Lago",
            "criterios": [
                {"nombre": "Área del Lago Glaciar", "descripcion": "Mayor área implica mayor volumen potencial de desbordamiento"},
                {"nombre": "Volumen del Lago Glaciar", "descripcion": "Directamente relacionado con la magnitud potencial de la inundación"},
                {"nombre": "Profundidad del Lago", "descripcion": "Influye en la estabilidad y la respuesta a impactos"},
                {"nombre": "Nivel de Borde Libre (Freeboard)", "descripcion": "Menor borde libre aumenta el riesgo de desbordamiento"}
            ]
        }
    },
    "F": {
        "nombre": "Factores Ambientales y de Contexto",
        "F.1": {
            "nombre": "Clima",
            "criterios": [
                {"nombre": "Temperatura", "descripcion": "Aumento acelera la fusión y la inestabilidad"},
                {"nombre": "Precipitación (Nieve y Lluvia)", "descripcion": "Lluvias intensas pueden contribuir a la fusión y desencadenar flujos de escombros"},
                {"nombre": "Eventos Climáticos Extremos", "descripcion": "Olas de calor, tormentas intensas"}
            ]
        },
        "F.2": {
            "nombre": "Geodinámica",
            "criterios": [
                {"nombre": "Actividad Sísmica", "descripcion": "Terremotos pueden desencadenar inestabilidad"},
                {"nombre": "Actividad Tectónica Regional", "descripcion": "Fallas activas cercanas"}
            ]
        },
        "F.3": {
            "nombre": "Cambios en el Tiempo",
            "criterios": [
                {"nombre": "Tasa de Crecimiento del Lago", "descripcion": "Rápida expansión indica mayor peligrosidad"},
                {"nombre": "Cambios en la Masa del Glaciar Padre", "descripcion": "Pérdida de masa puede aumentar la probabilidad de formación de lagos"}
            ]
        }
    },
    "G": {
        "nombre": "Susceptibilidad del Terreno Aguas Abajo",
        "G.1": {
            "nombre": "Impacto Potencial",
            "criterios": [
                {"nombre": "Pendiente del Valle Aguas Abajo", "descripcion": "Influye en la velocidad y alcance potencial de una inundación"},
                {"nombre": "Presencia de Constricciones o Embalsamientos Naturales", "descripcion": "Pueden modificar el flujo de la inundación"},
                {"nombre": "Tipo de Suelo y Cobertura Vegetal Aguas Abajo", "descripcion": "Influyen en la infiltración y la erosión potencial"}
            ]
        }
    }
}

# Guardar como archivo YAML
with open("../taxonomia_glaciares_completa.yaml", "w", encoding="utf-8") as f:
    yaml.dump(taxonomia_glaciares, f, allow_unicode=True, sort_keys=False)
