from data_access.interface import IDataReader
from typing import Union
import geopandas as gpd
import pandas as pd
import os

class GdbReader(IDataReader):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'path_gdb'):
            self.path_gdb = None

    def read_data(self, table_name:str) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        return gpd.read_file(self.path_gdb, layer = table_name)


    def validate_inputs(self):
        if self.path_gdb is None:
            raise("path_gdb is mandatory for GDB reader strategy")
        if not os.path.isdir(self.path_gdb):
            raise("path_gdb is not a folder")