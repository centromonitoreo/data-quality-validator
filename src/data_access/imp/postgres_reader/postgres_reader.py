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
        if not hasattr(self, 'geom_col'):
            self.geom_col = None

    def read_data(self, table_name: str) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        if table_name is None:
            return
        engine = create_engine(self.pg_conn_string)
        try:
            if self.geom_col:
                sql = f"SELECT * FROM {table_name}"
                df = gpd.read_postgis(sql, con=engine, geom_col=self.geom_col)
            else:
                df = pd.read_sql_table(table_name, con=engine)
            return df
        finally:
            engine.dispose()

    def validate_inputs(self):
        if not self.pg_conn_string:
            raise ("pg_conn_string is mandatory for Postgres reader strategy")

