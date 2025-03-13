
from validators.interface import IValidator
from validators.imp.duplicate_validator.schemas.schemas import DuplicatesIdentifyInput, DuplicatesIndentifyErrors, DuplicatesIdentifyError
import geopandas as gpd
from typing import Dict, Union
import pandas as pd
class DuplicatesIdentifyValidator(IValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'duplicates_identify_input'):
            self.duplicates_identify_input = None

    def validate(
        self, data: Union[pd.DataFrame, gpd.GeoDataFrame], **kwargs
    ) -> DuplicatesIndentifyErrors:
        #TODO implementar la validacion de duplicados
        self.validate_inputs()
        columns_to_check = self.duplicates_identify_input.columns
        duplicates = data.duplicated(subset=columns_to_check, keep=False)
        duplicated_data = data.loc[duplicates]
        errors = [
            DuplicatesIdentifyError(
                duplicate_index=duplicated_data.index.tolist(),
                duplicate_data=duplicated_data[col].astype(str).unique().tolist()
            )
            for col in columns_to_check if col in duplicated_data.columns
        ]
        return DuplicatesIndentifyErrors(list_errors=errors)
        # data.duplicated(subset=self.duplicates_identify_input)

    def validate_inputs(self) -> None:
        if self.duplicates_identify_input is None or not isinstance(self.duplicates_identify_input, DuplicatesIdentifyInput):
            raise ValueError(f"❌ ")

