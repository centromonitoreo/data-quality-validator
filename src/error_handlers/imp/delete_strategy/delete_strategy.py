from error_handlers.interface import IErrorHandler
from typing import Dict, Union
import geopandas as gpd
import pandas as pd
from error_handlers.imp.delete_strategy.schemas.schemas import DeleteErrorsInput, DeleteRows, DeleteData
import numpy as np

class DeleteErrorHandler(IErrorHandler):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'delete_errors_input'):
            self.delete_errors_input:DeleteErrorsInput = None

    def get_errors_from_thematic(self, table_name):
        for errors in self.delete_errors_input.errors:
            if errors.table_name == table_name:
                return errors

    def handle_table_error(
        self, data: Union[pd.DataFrame, gpd.GeoDataFrame], table_name: str
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        errors = self.get_errors_from_thematic(table_name)
        if isinstance(errors.errors, DeleteRows):
            data.drop(index=errors.errors.index, inplace=True)
        elif all(isinstance(e, DeleteData) for e in errors.errors):
            for error_data in errors.errors:
                column = error_data.column
                data.loc[error_data.index, column] = np.nan
        return data
    
    
    def handle_thematic_error(self, data_thematic: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]):
        for table_name, data in data_thematic.items():
            data_thematic[table_name] = self.handle_table_error(data, table_name)
        return data_thematic
    

    def validate_inputs(self):
        if self.delete_errors_input is None:
            raise("delete_errors_input is mandatory for the DeleteErrorHandler strategy")
        if not isinstance(self.delete_errors_input, DeleteErrorsInput):
             raise("delete_errors_input have to be a DeleteErrorsInput")
