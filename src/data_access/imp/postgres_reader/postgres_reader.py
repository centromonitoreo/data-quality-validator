from data_access.interface import IDataReader
from typing import Union
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
import os

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
            df = pd.read_sql_table(table_name.lower(), con=engine)
            mask = df["expediente"] == "LAM0019" # borrar
            df = df[mask] # borrar 
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

