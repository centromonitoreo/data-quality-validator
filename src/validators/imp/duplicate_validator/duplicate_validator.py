
from validators.interface import IValidator
from validators.imp.duplicate_validator.schemas.schemas import DuplicatesIdentifyInput, DuplicatesIdentifyErrors, DuplicatesIdentifyError
import geopandas as gpd
from validators.imp.duplicate_validator.adapters.delete_errors_handler_adapter import DeleteErrorHandlerAdapter
from error_handlers.imp.delete_strategy.delete_strategy import DeleteErrorHandler
from typing import Union
import pandas as pd


class DuplicatesIdentifyValidator(IValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'duplicates_identify_input'):
            self.duplicates_identify_input = None
            self.errors: DuplicatesIdentifyErrors = None

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

        self.errors = DuplicatesIdentifyErrors(list_errors=errors)

    def validate_inputs(self) -> None:
        """Validates that 'duplicates_identify_input' is of the correct type."""
        if self.duplicates_identify_input is None or not isinstance(self.duplicates_identify_input, DuplicatesIdentifyInput):
            raise ValueError(f"❌ Argumentos 'duplicates_identify_input' no son válidos.")


    def error_handler_adapter(self, error_hadler_strategy, table_name):
        if error_hadler_strategy == DeleteErrorHandler:
            return DeleteErrorHandlerAdapter(self.errors, table_name).adpter_erros()