from abc import ABC, abstractmethod
from typing import List, Dict, Union
from validators.interface import IValidator
from data_access.interface import IDataReader
import geopandas as gpd
import pandas as pd


class IRulesReader(ABC):

    def __init__(self, thematic: str):
        self.thematic = thematic
        

    @abstractmethod
    def get_validators(self, table:str) -> List[IValidator]:
        pass

    @abstractmethod
    def get_data(self, data_reader: IDataReader) -> Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]:
        pass

    @abstractmethod
    def get_validate_args(self, validator: IValidator):
        pass