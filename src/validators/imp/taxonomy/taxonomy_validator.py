from typing import Any, Dict
import datetime
import re
import time

import numpy as np
import pandas as pd
import pygbif
import requests
from fuzzywuzzy import fuzz
from multiprocess import Pool

from validators.interface import IValidator


def limpiar_texto(texto: str) -> str:
    """Clean a text value removing special characters and accents."""
    texto = re.sub(r"[.,-]", "", str(texto))
    texto = re.sub(r"\\([^)]*\\)", "", texto)
    texto = re.sub(r"\\d", "", texto)
    texto = re.sub(r"\\*", "", texto)
    texto = re.sub(r"\\?", "", texto)
    texto = re.sub(r"[áéíóúÁÉÍÓÚ]", "", texto)
    texto = texto.replace("morfo", "")
    texto = texto.replace("morfoespecie", "")
    texto = texto.replace("Morfoespecie", "")
    texto = texto.replace("mf", "")
    texto = texto.replace("subfamilia", "")
    texto = texto.replace('"', "")
    texto = texto.replace("‡", "")
    return texto


def words_delete(texto: str) -> str:
    palabras = texto.split()
    palabras_filtradas = [palabra for palabra in palabras if len(palabra) > 1]
    return " ".join(palabras_filtradas)


def limpiar_data(ruta_excel: str) -> pd.DataFrame:
    df = pd.read_csv(ruta_excel)

    nombre_genero = "GENERO"
    df[nombre_genero] = df[nombre_genero].str.lower()
    df[nombre_genero] = df[nombre_genero].apply(limpiar_texto)
    df[nombre_genero] = df[nombre_genero].apply(lambda x: " ".join(x.split()[:1]))
    df[nombre_genero] = df[nombre_genero].str.replace(
        r"\b(sp|cf|spp|aff|mf)\b", "", regex=True
    )

    nombre_especie = "ESPECIE"
    df[nombre_especie] = df[nombre_especie].str.lower()
    df[nombre_especie] = df[nombre_especie].apply(limpiar_texto)
    df[nombre_especie] = df[nombre_especie].apply(lambda x: " ".join(x.split()[:2]))
    df[nombre_especie] = df[nombre_especie].apply(words_delete)

    df["especie_original"] = df[nombre_especie]

    df[nombre_especie] = df[nombre_especie].str.replace(
        r"\b(sp|cf|spp|aff|mf)\b", "", regex=True
    )

    return df


def contar_palabras_y_modificar(row: pd.Series) -> pd.Series:
    if (isinstance(row["ESPECIE"], str)) & (isinstance(row["GENERO"], str)):
        especie = row["ESPECIE"]
        genero = row["GENERO"]
        palabras_especie = especie.split()
        if (len(palabras_especie) == 1) & (not pd.isna(genero)):
            especie = genero + " " + especie
        return especie
    return row["ESPECIE"]


def ajustar_genero(df: pd.DataFrame) -> pd.DataFrame:
    df["ESPECIE"].fillna("", inplace=True)
    df["GENERO"].fillna("", inplace=True)
    df["ESPECIE"] = df["ESPECIE"].replace({"nan": np.nan})
    df["GENERO"].fillna("", inplace=True)
    df["GENERO"] = df["GENERO"].replace({"nan": np.nan})
    df["ESPECIE"] = df.apply(contar_palabras_y_modificar, axis=1)
    return df


def probar_conexion():
    time_inicio = datetime.datetime.today()
    while 1 == 1:
        try:
            requests.get("http://www.google.com", timeout=5)
            return True
        except (requests.ConnectionError, requests.Timeout):
            timepo_step = datetime.datetime.today()
            _ = (timepo_step - time_inicio).seconds
            time.sleep(5)
    return False


def evaluar_alternativa(alternativa, dict_taxonomia):
    lista_nombres_definitivos = {
        "class": "CLASE",
        "order": "ORDEN",
        "family": "FAMILIA",
        "genus": "GENERO",
        "species": "ESPECIE",
    }
    dict_evaluacion = {}
    for taxonomia, _ in lista_nombres_definitivos.items():
        nombre = alternativa.get(taxonomia, None)
        correlacion_max = 0
        taxon_relacion = ""
        if not nombre is None:
            for taxon_usuario, nombre_usuario in dict_taxonomia.items():
                nombre_usuario = (
                    nombre_usuario if isinstance(nombre_usuario, str) else "No aplica"
                )
                correlacion = fuzz.ratio(nombre_usuario.lower(), nombre.lower())
                if correlacion > correlacion_max:
                    correlacion_max = correlacion
                    taxon_relacion = taxon_usuario
            dict_evaluacion[taxonomia] = {
                "correlacion_max": correlacion_max,
                "taxon_relacion": taxon_relacion,
                "nombre_sugerido": nombre,
            }
        else:
            dict_evaluacion[taxonomia] = {
                "correlacion_max": 0,
                "taxon_relacion": "error",
                "nombre_sugerido": nombre,
            }
    dict_evaluacion["Alternativa"] = alternativa
    return dict_evaluacion


def gbif_rev(taxonomia, nivel_taxonomia, dict_taxonomia):
    dict_permitidos = {
        "order": ["order", "family"],
        "family": ["genus", "family", "order"],
        "genus": ["genus", "family"],
        "species": ["species"],
    }

    list_alternativas = []
    species_busqueda = pygbif.species.name_backbone(name=taxonomia, verbose=True)
    if not species_busqueda["matchType"] == "NONE" or "alternatives" in list(
        species_busqueda.keys()
    ):
        alternativas = species_busqueda.get("alternatives", None)
        if not alternativas is None:
            for alternativa in alternativas:
                if alternativa["rank"].lower() in dict_permitidos[nivel_taxonomia]:
                    dict_alternativa = evaluar_alternativa(alternativa, dict_taxonomia)
                    list_alternativas.append(dict_alternativa)
            if (
                species_busqueda.get("rank", "").lower()
                in dict_permitidos[nivel_taxonomia]
            ):
                dict_alternativa = evaluar_alternativa(species_busqueda, dict_taxonomia)
                list_alternativas.append(dict_alternativa)
        else:
            if (
                species_busqueda.get("rank", "").lower()
                in dict_permitidos[nivel_taxonomia]
            ):
                dict_alternativa = evaluar_alternativa(species_busqueda, dict_taxonomia)
                list_alternativas.append(dict_alternativa)
    return list_alternativas


def calificar_alternativa(alternativa, dict_taxonomia):
    taxon_menor = None
    taxon_mayor = None
    for taxon, valor_taxon in dict_taxonomia.items():
        if not pd.isna(valor_taxon):
            if taxon_menor is None:
                taxon_menor = taxon
            else:
                taxon_mayor = taxon

    dict_pesos = {}
    for taxon, _ in dict_taxonomia.items():
        dict_pesos[taxon] = 3 if taxon in [taxon_menor, taxon_mayor] else 1

    suma_alternativa = 0
    for taxonomia, valor in alternativa.items():
        if taxonomia in dict_pesos.keys():
            if (taxonomia != "Alternativa") & (valor is not None):
                suma_alternativa += valor["correlacion_max"] * dict_pesos[taxonomia]
    suma_alternativa = suma_alternativa / sum(list(dict_pesos.values()))
    return suma_alternativa


def seleccionar_mejor_alternativa(dict_result, dict_taxonomia):
    puntaje_mejor_alternativa = 0
    mejor_alternativa = {}
    for _, alternativas_taxon in dict_result.items():
        for alternativa_taxon in alternativas_taxon:
            if (
                calificar_alternativa(alternativa_taxon, dict_taxonomia)
                > puntaje_mejor_alternativa
            ):
                puntaje_mejor_alternativa = calificar_alternativa(
                    alternativa_taxon, dict_taxonomia
                )
                mejor_alternativa = alternativa_taxon
    return mejor_alternativa, puntaje_mejor_alternativa


def taxonomy_validation(argumentos: list) -> dict:
    try:
        key_fila, dict_taxonomia = argumentos
        dict_result = {}
        for nivel_taxonomia, taxonomia in dict_taxonomia.items():
            dict_result[nivel_taxonomia] = gbif_rev(
                taxonomia, nivel_taxonomia, dict_taxonomia
            )
        mejor_alternativa, coor = seleccionar_mejor_alternativa(
            dict_result, dict_taxonomia
        )
        return {
            key_fila: {
                "alternativa": mejor_alternativa["Alternativa"],
                "coor": coor,
                "datos_iniciales": dict_taxonomia,
            }
        }
    except Exception as e:
        return {
            key_fila: {
                "alternativa": {
                    "class": np.nan,
                    "order": np.nan,
                    "family": np.nan,
                    "genus": np.nan,
                    "species": np.nan,
                },
                "coor": e,
                "datos_iniciales": dict_taxonomia,
            }
        }


def procesar_taxonomia(biotico: pd.DataFrame) -> dict:
    lista_nombres_definitivos = {
        "order": "ORDEN",
        "family": "FAMILIA",
        "genus": "GENERO",
        "species": "ESPECIE",
    }
    lista_argumentos = []
    for key_fila, row in biotico.iterrows():
        dict_taxonomia = {}
        for key, value in lista_nombres_definitivos.items():
            dict_taxonomia[key] = row[value]
        lista_argumentos.append((key_fila, dict_taxonomia))

    pool = Pool(processes=16)
    result = pool.map(taxonomy_validation, lista_argumentos)
    pool.close()
    pool.join()
    return result


def taxonomy_revision(fila_path: str) -> pd.DataFrame:
    # Limpiar y ajustar los datos
    df_limpio_data = limpiar_data(fila_path)
    df_genero_limpio = ajustar_genero(df_limpio_data)

    # Crear una copia de los datos limpios para procesamiento adicional
    biotico = df_genero_limpio.copy()

    # Definir las columnas que se van a actualizar con NaN
    columns_to_update = [
        "CLASE_SU",
        "ORDEN_SU",
        "FAMILIA_SU",
        "GENERO_SU",
        "ESPECIE_SU",
        "usageKey",
        "CORR",
    ]
    biotico[columns_to_update] = np.nan

    # Definir las combinaciones unicas de taxonomia
    taxonomy_columns = [
        "CLASE",
        "ORDEN",
        "FAMILIA",
        "GENERO",
        "ESPECIE",
        "CLASE_SU",
        "ORDEN_SU",
        "FAMILIA_SU",
        "GENERO_SU",
        "ESPECIE_SU",
    ]

    df_unicos = (
        biotico[taxonomy_columns].fillna("Sin Dato").value_counts().reset_index()
    )

    # Ejecutar la función principal con los resultados únicos
    resultados = procesar_taxonomia(df_unicos)

    biotico = biotico[taxonomy_columns].fillna("Sin Dato")

    for dict_result_fila in resultados:
        for key_fila, resultado in dict_result_fila.items():
            dict_resultado = resultado["datos_iniciales"]
            for taxonomia, nombre in dict_resultado.items():
                dict_resultado[taxonomia] = (
                    nombre if not pd.isna(nombre) else "Sin Dato"
                )
            biotico.loc[
                (
                    (biotico["FAMILIA"] == dict_resultado["family"])
                    & (biotico["GENERO"] == dict_resultado["genus"])
                    & (biotico["ESPECIE"] == dict_resultado["species"])
                ),
                "REINO",
            ] = resultado["alternativa"].get("kingdom", np.nan)
            biotico.loc[
                (
                    (biotico["FAMILIA"] == dict_resultado["family"])
                    & (biotico["GENERO"] == dict_resultado["genus"])
                    & (biotico["ESPECIE"] == dict_resultado["species"])
                ),
                "CLASE_SU",
            ] = resultado["alternativa"].get("class", np.nan)
            biotico.loc[
                (
                    (biotico["FAMILIA"] == dict_resultado["family"])
                    & (biotico["GENERO"] == dict_resultado["genus"])
                    & (biotico["ESPECIE"] == dict_resultado["species"])
                ),
                "ORDEN_SU",
            ] = resultado["alternativa"].get("order", np.nan)
            biotico.loc[
                (
                    (biotico["FAMILIA"] == dict_resultado["family"])
                    & (biotico["GENERO"] == dict_resultado["genus"])
                    & (biotico["ESPECIE"] == dict_resultado["species"])
                ),
                "FAMILIA_SU",
            ] = resultado["alternativa"].get("family", np.nan)
            biotico.loc[
                (
                    (biotico["FAMILIA"] == dict_resultado["family"])
                    & (biotico["GENERO"] == dict_resultado["genus"])
                    & (biotico["ESPECIE"] == dict_resultado["species"])
                ),
                "GENERO_SU",
            ] = resultado["alternativa"].get("genus", np.nan)
            biotico.loc[
                (
                    (biotico["FAMILIA"] == dict_resultado["family"])
                    & (biotico["GENERO"] == dict_resultado["genus"])
                    & (biotico["ESPECIE"] == dict_resultado["species"])
                ),
                "ESPECIE_SU",
            ] = resultado["alternativa"].get("species", np.nan)
            biotico.loc[
                (
                    (biotico["FAMILIA"] == dict_resultado["family"])
                    & (biotico["GENERO"] == dict_resultado["genus"])
                    & (biotico["ESPECIE"] == dict_resultado["species"])
                ),
                "CORREL",
            ] = resultado["coor"]

    biotico = biotico.replace({"Sin Dato": np.nan})
    biotico["CORREL"] = biotico["CORREL"].apply(lambda x: x if isinstance(x, float) else 0)
    return biotico


class TaxonomyValidator(IValidator):
    def __init__(self):
        super().__init__()

    def validate(self, data: Dict[str, Any]):
        """Validate taxonomy information contained in ``data``.

        Parameters
        ----------
        data: Dict[str, Any]
            Path to a CSV file with taxonomy columns.

        Returns
        -------
        pd.DataFrame
            Dataframe with the suggested taxonomy.
        """

        return taxonomy_revision(data)

    def validate_inputs(self):
        return super().validate_inputs()

