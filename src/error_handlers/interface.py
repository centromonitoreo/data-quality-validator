from abc import ABC, abstractmethod
from typing import Dict, Union
import geopandas as gpd
import pandas as pd


class IErrorHandler(ABC):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def handle_table_error(
        self, data_table: Union[pd.DataFrame, gpd.GeoDataFrame]
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        pass

    @abstractmethod
    def handle_thematic_error(
        self, data_thematic: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]
    ) -> Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]:
        pass

    
    @abstractmethod
    def validate_inputs(self) -> None:
        pass
