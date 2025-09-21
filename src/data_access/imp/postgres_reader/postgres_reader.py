import os
from typing import Union

import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text, bindparam
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String

from data_access.interface import IDataReader


EXPEDIENTES = [
    "LAM0237",
    "LAM4037",
    "LAM0112",
    "LAM2583",
    "LAM2577",
    "LAM2142",
    "LAM3575",
    "LAM3823",
    "LAM2578",
    "LAM2575",
    "LAM2574",
    "LAM3888",
    "LAM2576",
    "LAM4090",
    "LAM0005",
    "LAM0514",
    "LAM1582",
    "LAM2230",
    "LAM2233",
    "LAM2582",
    "LAM2611",
    "LAM2223",
    "LAM0529",
    "LAM0261",
    "LAM4697",
    "LAM0058",
    "LAM2581",
    "LAM3948",
    "LAM3563",
    "LAV0021-00-2021",
    "LAM9086-00",
    "LAV0070-00-2017",
    "LAM1094",
    "LAM3491",
    "LAM2622",
    "LAM5801",
    "LAM3831",
    "LAM1862",
    "LAM5688",
    "LAV0029-00-2016",
    "LAM3271",
    "LAM0027",
    "LAM3199",
    "LAM1748",
    "LAM6086",
    "LAM4031",
    "LAM0408",
    "LAM1203",
    "LAV0018-00-2015",
    "LAM1403",
    "LAM1499",
    "LAM6153",
    "LAM0579",
    "LAM0806",
    "LAM0530",
    "LAM0626",
    "LAM4567",
    "LAM2347",
    "LAV0050-13",
    "LAM4924",
    "LAM1821",
    "LAM3830",
    "LAV0052-00-2019",
    "LAV0002-00-2020",
    "LAM8418-00",
    "LAM9389-00",
    "LAM9139-00",
    "LAV0012-00-2023",
    "LAM9182-00",
    "LAV0034-00-2023",
]

expedientes = EXPEDIENTES


class PostgresReader(IDataReader):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'pg_conn_string'):
            self.pg_conn_string = os.getenv('PG_DATABASE_URL')

    def read_data(self, table_name: str) -> Union[pd.DataFrame, gpd.GeoDataFrame]:

        if not table_name:
            return

        engine = create_engine(self.pg_conn_string)
        try:
            filter_values = getattr(self, "expediente", None)
            if filter_values is None:
                filter_values = getattr(self, "expedientes", EXPEDIENTES)

            if isinstance(filter_values, str):
                filter_values = [filter_values]

            if filter_values:
                stmt = (
                    text(
                        f"""SELECT * FROM {table_name.lower()} WHERE expediente = ANY(:exp)"""
                    )
                    .bindparams(
                        bindparam("exp", value=filter_values, type_=ARRAY(String))
                    )
                )
            else:
                stmt = text(f"SELECT * FROM {table_name.lower()}")
            df = pd.read_sql_query(stmt, con=engine)
            if "geometry" in df.columns:

                geom_series = df["geometry"]

                # Caso A: ya vienen como objetos shapely (tienen atributo geom_type)
                non_null = geom_series.dropna()
                if not non_null.empty and getattr(non_null.iloc[0], "geom_type", None) is not None:
                    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
                    return gdf.to_crs(9377)

                # Caso B: intentar WKB (bytes/memoryview o hex)
                def _to_wkb_bytes(v):
                    # memoryview/bytes directos
                    if isinstance(v, (bytes, bytearray, memoryview)):
                        return bytes(v)
                    # cadenas que podrían ser hex (con o sin '0x')
                    if isinstance(v, str):
                        s = v.strip()
                        if s.startswith("0x") or all(c in "0123456789abcdefABCDEF" for c in s.replace(" ", "")[:10]):
                            try:
                                s = s[2:] if s.lower().startswith("0x") else s
                                return bytes.fromhex(s)
                            except Exception:
                                return None
                    return None

                try:
                    # Intento 1: WKB directo (acepta bytes/memoryview)
                    parsed = gpd.GeoSeries.from_wkb(geom_series)
                except Exception:
                    # Intento 2: convertir posibles hex a bytes y reintentar WKB
                    try:
                        wkb_bytes = geom_series.where(geom_series.notna(), None).apply(_to_wkb_bytes)
                        parsed = gpd.GeoSeries.from_wkb(wkb_bytes)
                    except Exception:
                        # Intento 3: WKT
                        parsed = gpd.GeoSeries.from_wkt(geom_series.astype("string"))

                gdf = gpd.GeoDataFrame(
                    df.drop(columns=["geometry"], errors="ignore"),
                    geometry=parsed,
                    crs="EPSG:4326"  # Cambia aquí si tu SRID no es 4326
                )
                return gdf.to_crs(9377)

            # Si no hay columna 'geometry', retornar DataFrame normal
            return df

        finally:
            engine.dispose()

    def validate_inputs(self):
        if not self.pg_conn_string:
            raise ("pg_conn_string is mandatory for Postgres reader strategy")

