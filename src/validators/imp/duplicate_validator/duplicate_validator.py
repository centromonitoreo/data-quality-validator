
from validators.interface import IValidator
from validators.imp.duplicate_validator.schemas.schemas import DuplicatesIdentifyInput
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
    ) :
        data.duplicated(subset=self.duplicates_identify_input)

    def validate_inputs(self) -> None:
        if self.duplicates_identify_input is None or not isinstance(self.duplicates_identify_input, DuplicatesIdentifyInput):
            raise ValueError(f"❌ ")

