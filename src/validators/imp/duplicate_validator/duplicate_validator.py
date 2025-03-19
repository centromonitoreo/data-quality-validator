
from validators.interface import IValidator
from validators.imp.duplicate_validator.schemas.schemas import DuplicatesIdentifyInput, DuplicatesIdentifyErrors, DuplicatesIdentifyError
import geopandas as gpd
from typing import Union
import pandas as pd


class DuplicatesIdentifyValidator(IValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'duplicates_identify_input'):
            self.duplicates_identify_input = None

    def validate(
        self, data: Union[pd.DataFrame, gpd.GeoDataFrame], **kwargs
    ) -> DuplicatesIdentifyErrors:
        """."""

        columns_to_check = self.duplicates_identify_input.columns

        duplicates = data.duplicated(subset=columns_to_check, keep=False)
        duplicated_data = data.loc[duplicates]
        grouped_duplicated_data = duplicated_data.groupby(columns_to_check).apply(lambda x: x.index.tolist())

        errors = [
            DuplicatesIdentifyError(
                duplicate_index=indexes,
                duplicate_data={col: key[i] for i, col in enumerate(columns_to_check)}
            )
            for key, indexes in grouped_duplicated_data.items()
        ]

        return DuplicatesIdentifyErrors(list_errors=errors)

    def validate_inputs(self) -> None:
        """Validates that 'duplicates_identify_input' is of the correct type."""
        if self.duplicates_identify_input is None or not isinstance(self.duplicates_identify_input, DuplicatesIdentifyInput):
            raise ValueError(f"❌ Argumentos 'duplicates_identify_input' no son válidos.")

