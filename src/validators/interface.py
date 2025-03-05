from abc import ABC, abstractmethod
from typing import Dict, Union
import geopandas as gpd
import pandas as pd

class IValidator(ABC):


    @abstractmethod
    def validate(
        self, data: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]
    ) -> Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]:
        pass