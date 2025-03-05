from abc import ABC, abstractmethod
from typing import Dict, Union
import geopandas as gpd
import pandas as pd


class IErrorHandler(ABC):

    @abstractmethod
    def handle(
        self, data: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]
    ) -> Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]:
        pass
