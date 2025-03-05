from error_handlers.interface import IErrorHandler
from typing import Dict, Union
import geopandas as gpd
import pandas as pd


class DeleteErrorHandler(IErrorHandler):

    def handle(
        self, data: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]
    ) -> Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]:
        pass
