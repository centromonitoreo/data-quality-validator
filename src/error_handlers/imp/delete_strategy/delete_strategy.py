from error_handlers.interface import IErrorHandler
from typing import Dict, Union
import geopandas as gpd
import pandas as pd
from error_handlers.imp.delete_strategy.schemas.schemas import DeleteErrorsInput
import numpy as np

class DeleteErrorHandler(IErrorHandler):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'duplicates_identify_input'):
            self.delete_errors_input:DeleteErrorsInput = None

    def get_errors_from_thematic(self, table_name):
        for errors in self.delete_errors_input.errors:
            if errors.table_name == table_name:
                return errors

    def handle_table_error(
        self, data: Union[pd.DataFrame, gpd.GeoDataFrame], table_name: str
    ) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        errors = self.get_errors_from_thematic(table_name)
        if isinstance(errors, list):
            for error_column in errors:
                column = error_column.column
                data.loc[error_column.index, column] = np.nan
        else:
            data.drop(index=errors.index, inplace=True)
        return data
    
    
    def handle_thematic_error(self, data_thematic: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]):
        for table_name, data in data_thematic.items():
            data_thematic[table_name] = self.handle_table_error(data, table_name)
        return data_thematic
    

    def validate_inputs(self):
        if self.delete_errors_input is None:
            raise("delete_errors_input is mandatory for the DeleteErrorHandler strategy")
        if not isinstance(self.delete_errors_input, DeleteErrorHandler):
             raise("delete_errors_input have to be a DeleteErrorsInput")
