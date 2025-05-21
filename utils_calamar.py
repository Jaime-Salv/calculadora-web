
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_calamar.json")

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
        "total_plastico_kg": 0,
        "total_coste_plastico": 0,
        "pn_entrada_especie": {},
        "aditivos": {},
        "filas": []
    }

    total_C = 0
    total_plastico_gramos = 0

    for fila in datos:
        especie = fila["especie"]
        formato = fila["formato"]
        formato_real = "4CJ" if formato == "CG" else formato
        kg_in = fila["kg_entrada"]
        cajas = fila["cajas"]
        palets = fila["palets"]
        lamina = fila["lamina"]

        destare_val = config["destare"].get(formato, 0)
        pn_entrada = kg_in - (cajas * destare_val + palets)
        resultados["pn_entrada_especie"][especie] = resultados["pn_entrada_especie"].get(especie, 0) + pn_entrada

        gramos_producto = config["tabla_1"].get(especie, {}).get(formato_real, 0)
        gramos_lamina = config["plastico_laminas"].get(formato_real, 0)
        gramos_totales_fila = (gramos_producto + gramos_lamina) * cajas
        kg_plastico_fila = gramos_totales_fila / 1000

        total_plastico_gramos += gramos_totales_fila
        total_C += gramos_totales_fila

        precio_3 = config["tabla_3"].get(especie, {}).get(formato_real, 0)
        lamina_data = config["tabla_4"].get(lamina, {})
        base = lamina_data.get("base", 0)
        ajuste = lamina_data.get("ajustes", {}).get(formato_real, 0)
        precio_4 = base * ajuste
        coste_total_fila = (precio_3 + precio_4) * cajas

        resultados["total_coste_plastico"] += coste_total_fila
        resultados["total_cajas"] += cajas

        resultados["filas"].append({
            "especie": especie,
            "formato": formato,
            "pn_entrada": pn_entrada,
            "kg_plastico": kg_plastico_fila,
            "coste_plastico": coste_total_fila
        })

    resultados["total_plastico_kg"] = total_plastico_gramos / 1000
    resultados["plastico_por_caja"] = (total_C / resultados["total_cajas"]) / 1000 if resultados["total_cajas"] > 0 else 0

    for nombre, datos_aditivo in config["aditivos"].items():
        porcentaje = datos_aditivo.get("porcentaje", 0)
        precio_kg = datos_aditivo.get("precio_kg", 0)
        cantidad = pn_salida_total * porcentaje
        coste = cantidad * precio_kg
        resultados["aditivos"][nombre] = {"kg": round(cantidad, 2), "euro": round(coste, 2)}

    return resultados
