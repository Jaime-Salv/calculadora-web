
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_pulpo.json")

def cargar_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def guardar_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)

CONFIG_DATA = cargar_config()

def calcular_resultado(datos, pn_salida_total):
    config = CONFIG_DATA
    resultados = {
        "total_cajas": 0,
        "total_coste_plastico": 0,
        "pn_entrada_especie": {},
        "aditivos": {},
        "filas": []
    }

    for fila in datos:
        especie = fila["especie"]
        formato = fila["formato"]
        kg_in = fila["kg_entrada"]
        cajas = fila["cajas"]
        palets = fila["palets"]

        destare_val = config["destare"].get(formato, 0)
        pn_entrada = kg_in - (cajas * destare_val + palets)
        resultados["pn_entrada_especie"][especie] = resultados["pn_entrada_especie"].get(especie, 0) + pn_entrada

        precio_formato = config["tabla_3"].get(especie, {}).get(formato, 0)
        coste_total_fila = precio_formato * cajas
        resultados["total_coste_plastico"] += coste_total_fila
        resultados["total_cajas"] += cajas

        # Suponemos 100 gramos de plástico por caja como valor genérico
        kg_plastico_fila = config.get("plástico_promedio_kg_por_caja", 0.1) * cajas

        resultados["filas"].append({
            "especie": especie,
            "formato": formato,
            "pn_entrada": pn_entrada,
            "kg_plastico": kg_plastico_fila,
            "coste_plastico": coste_total_fila
        })

    for nombre, datos_ad in config["aditivos"].items():
        porcentaje = datos_ad["porcentaje"]
        precio_kg = datos_ad["precio_kg"]
        cantidad = pn_salida_total * porcentaje
        coste = cantidad * precio_kg
        resultados["aditivos"][nombre] = {"kg": round(cantidad, 2), "euro": round(coste, 2)}

    return resultados
