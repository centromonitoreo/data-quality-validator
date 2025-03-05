from abc import ABC, abstractmethod
from typing import Union
import geopandas as gpd
import pandas as pd

class IDataReader(ABC):

    @abstractmethod
    def read_data(self, thematic:str) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        pass