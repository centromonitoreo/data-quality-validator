from abc import ABC, abstractmethod
from typing import Union, Dict
import geopandas as gpd
import pandas as pd

class IDataReader(ABC):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def read_data(self, table_name:str) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        pass

    @abstractmethod
    def validate_inputs(self) -> None:
        pass