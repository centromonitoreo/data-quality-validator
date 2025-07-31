import os
from typing import Union

import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text, bindparam
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String

from data_access.interface import IDataReader


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
            expedientes = ['LAM0019','LAM0165','LAM0226','LAM0471','LAM0472','LAM1235',
                       'LAM1437','LAM1700','LAM1959','LAM2016','LAM2680','LAM2957',
                       'LAM2965','LAM2997','LAM3094','LAM3095','LAM3261','LAM3293',
                       'LAM3338','LAM3340','LAM3341','LAM3524','LAM3547','LAM3548',
                       'LAM3585','LAM3590','LAM3592','LAM3605','LAM3629','LAM3657',
                       'LAM3678','LAM3739','LAM3786','LAM3847','LAM3941','LAM3969',
                       'LAM4008','LAM4096','LAM4221','LAM4282','LAM4352','LAM4489',
                       'LAM4502','LAM4503','LAM4510','LAM4511','LAM4597','LAM4649',
                       'LAM4700','LAM4707','LAM4795','LAM4887','LAM4973','LAM4978',
                       'LAM4983','LAM5023','LAM5088','LAM5089','LAM5104','LAM5124',
                       'LAM5129','LAM5170','LAM5172','LAM5175','LAM5225','LAM5281',
                       'LAM5297','LAM5475','LAM5506','LAM5557','LAM5764','LAM5787',
                       'LAM5815','LAM5836','LAM5995','LAV0006-00-2021','LAV0006-12',
                       'LAV0011-14','LAV0012-00-2018','LAV0013-00-2023','LAV0021-00-2023',
                       'LAV0030-14','LAV0033-00-2015','LAV0033-00-2018','LAV0034-00-2015',
                       'LAV0035-00-2015','LAV0037-00-2015','LAV0041-13','LAV0043-14',
                       'LAV0048-00-2015','LAV0049-00-2015','LAV0078-00-2021','LAV0084-13',
                       'LAV0090-00-2014',]
            stmt = text(f"""SELECT * FROM {table_name.lower()} WHERE expediente = ANY(:exp)""").bindparams(bindparam("exp", value=expedientes, type_=ARRAY(String)))
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

