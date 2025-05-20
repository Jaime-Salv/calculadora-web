
from flask import Flask, render_template, request, redirect
from utils_calamar import calcular_resultado as calcular_calamar, cargar_config as cargar_config_calamar, guardar_config as guardar_config_calamar
from utils_pulpo import calcular_resultado as calcular_pulpo, cargar_config as cargar_config_pulpo, guardar_config as guardar_config_pulpo

app = Flask(__name__)

@app.route("/")
def menu():
    return render_template("index.html")

@app.route("/calamar", methods=["GET", "POST"])
def calamar():
    resultado = None
    datos = []
    pn_salida = ""
    if request.method == "POST":
        try:
            especies = request.form.getlist("especie[]")
            formatos = request.form.getlist("formato[]")
            laminas = request.form.getlist("lamina[]")
            kg_entradas = request.form.getlist("kg_entrada[]")
            cajas = request.form.getlist("cajas[]")
            palets = request.form.getlist("palets[]")
            pn_salida = float(request.form["pn_salida"])
            for i in range(len(especies)):
                fila = {
                    "especie": especies[i],
                    "formato": formatos[i],
                    "lamina": laminas[i],
                    "kg_entrada": float(kg_entradas[i]),
                    "cajas": int(cajas[i]),
                    "palets": float(palets[i])
                }
                datos.append(fila)
            resultado = calcular_calamar(datos, pn_salida)
        except Exception as e:
            resultado = {"error": str(e)}
    return render_template("calamar.html", resultado=resultado, datos=datos, pn_salida=pn_salida)

@app.route("/editar-calamar", methods=["GET", "POST"])
def editar_calamar():
    config = cargar_config_calamar()
    if request.method == "POST":
        nuevo_config = procesar_formulario(request.form)
        guardar_config_calamar(nuevo_config)
        return redirect("/editar-calamar")
    return render_template("editar_config_calamar.html", config=config)

@app.route("/pulpo", methods=["GET", "POST"])
def pulpo():
    resultado = None
    datos = []
    pn_salida = ""
    if request.method == "POST":
        try:
            especies = request.form.getlist("especie[]")
            formatos = request.form.getlist("formato[]")
            kg_entradas = request.form.getlist("kg_entrada[]")
            cajas = request.form.getlist("cajas[]")
            palets = request.form.getlist("palets[]")
            pn_salida = float(request.form["pn_salida"])
            for i in range(len(especies)):
                fila = {
                    "especie": especies[i],
                    "formato": formatos[i],
                    "kg_entrada": float(kg_entradas[i]),
                    "cajas": int(cajas[i]),
                    "palets": float(palets[i])
                }
                datos.append(fila)
            resultado = calcular_pulpo(datos, pn_salida)
        except Exception as e:
            resultado = {"error": str(e)}
    return render_template("pulpo.html", resultado=resultado, datos=datos, pn_salida=pn_salida)

@app.route("/editar-pulpo", methods=["GET", "POST"])
def editar_pulpo():
    config = cargar_config_pulpo()
    if request.method == "POST":
        nuevo_config = procesar_formulario(request.form)
        guardar_config_pulpo(nuevo_config)
        return redirect("/editar-pulpo")
    return render_template("editar_config_pulpo.html", config=config)

def procesar_formulario(form):
    nuevo_config = {
        "destare": {},
        "tabla_3": {},
        "aditivos": {},
        "tabla_1": {},
        "plastico_laminas": {},
        "tabla_4": {}
    }
    for key, value in form.items():
        if key.startswith("destare_"):
            k = key.replace("destare_", "")
            nuevo_config["destare"][k] = float(value)
        elif key.startswith("plastico_laminas_"):
            k = key.replace("plastico_laminas_", "")
            nuevo_config["plastico_laminas"][k] = float(value)
        elif key.startswith("tabla1_"):
            especie, formato = key.replace("tabla1_", "").split("__")
            nuevo_config["tabla_1"].setdefault(especie, {})[formato] = float(value)
        elif key.startswith("tabla3_"):
            especie, formato = key.replace("tabla3_", "").split("__")
            nuevo_config["tabla_3"].setdefault(especie, {})[formato] = float(value)
        elif key.startswith("tabla4_"):
            partes = key.replace("tabla4_", "").split("__")
            lamina = partes[0]
            if partes[1] == "base":
                nuevo_config["tabla_4"].setdefault(lamina, {"base": 0, "ajustes": {}})
                nuevo_config["tabla_4"][lamina]["base"] = float(value)
            elif partes[1] == "ajuste":
                formato = partes[2]
                nuevo_config["tabla_4"].setdefault(lamina, {"base": 0, "ajustes": {}})
                nuevo_config["tabla_4"][lamina]["ajustes"][formato] = float(value)
        elif key.startswith("aditivos_"):
            nombre, campo = key.replace("aditivos_", "").split("__")
            nuevo_config["aditivos"].setdefault(nombre, {})[campo] = float(value)
    return nuevo_config

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

