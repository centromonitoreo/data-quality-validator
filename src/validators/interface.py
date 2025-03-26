from abc import ABC, abstractmethod
from typing import Dict, Union
import geopandas as gpd
import pandas as pd
from error_handlers.interface import IErrorHandler

class IValidator(ABC):
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def validate(
        self, data: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]], **kwargs
    ) -> Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]:
        pass

    @abstractmethod
    def validate_inputs(self) -> None:
        pass


    @abstractmethod
    def error_handler_adapter(self, error_hadler_strategy:IErrorHandler):
        pass