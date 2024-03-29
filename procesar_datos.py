import pandas as pd

def cargar_fichero(path: str, column:str) -> list:
    df = pd.read_csv(
        path,
        index_col=0,
        parse_dates=["fecha_ingreso", "fecha_egreso", "fecha_ing_uci", "fecha_egr_uci"],
    )
    df["tiempo_vam"] = df["tiempo_vam"].astype(int)
    df["diagnostico_preuci"] = df["diagnostico_preuci"].astype("category")
    estadia = list(df.sort_values("fecha_ingreso")[column])
    return estadia
def get_fecha_ingreso(path: str):

    fecha_ingreso = cargar_fichero(path, "fecha_ingreso")
    fecha = fecha_ingreso[0]

    for fecha_siguiente in fecha_ingreso:
        yield (fecha_siguiente, fecha)
        fecha = fecha_siguiente

def get_fecha_egreso(path: str):

    fecha_ingreso = cargar_fichero(path, "fecha_egreso")
    for fecha in fecha_ingreso:
        yield fecha

def get_fecha_ing_uci(path: str):

    fecha_ingreso = cargar_fichero(path, "fecha_ing_uci")
    for fecha in fecha_ingreso:
        yield fecha

def get_tiempo_vam(path:str):

    tiempo_vam = cargar_fichero(path, "tiempo_vam")
    for horas in  tiempo_vam:
        yield horas

def get_fecha_egr_uci(path: str):

    fecha_ingreso = cargar_fichero(path, "fecha_egr_uci")
    for fecha in fecha_ingreso:
        yield fecha

def get_estadia_uci(path: str):

    estadia = cargar_fichero(path, "estadia_uci")
    for est in estadia:
        yield est

def get_sala_egreso(path: str):

    salas = cargar_fichero(path, "sala_egreso")
    for sala in salas:
        yield sala

def get_evolucion(path: str):

    evoluciones = cargar_fichero(path, "evolucion")
    for evolucion in evoluciones:
        yield evolucion

def get_diagnostico(path: str):

    diagnosticos = cargar_fichero(path, "diagnostico_preuci")
    for daignostico in diagnosticos:
        yield daignostico

def get_diagnostico_list(path: str):
    df = pd.read_csv(path)
    diagnostico_list = df["diagnostico_preuci"].unique()
    return diagnostico_list