from validators.interface import IValidator
from validators.imp.field_validator.schemas.schemas import FieldTypeVerificationError, ErrorType, MandatoryErrorData, FieldTypeVerification
import pandas as pd
from typing import Union
import geopandas as gpd
from rule_access.imp.database_reader.config import engine


class MandatoryVerificationValidator(IValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'fields_type_verification'):
            self.fields_type_verification = None

    def validate_mandatory(self, values: pd.Series, column_name) -> FieldTypeVerificationError:
        data_errors = values[values.isnull() | values.isna()]

        if len(data_errors) == 0:
            return None
        
        return FieldTypeVerificationError(
            column=column_name,
            error_type=ErrorType.mandatory_error,
            error_data=MandatoryErrorData(list_index=data_errors.index.tolist())
        )
    
    def validate(
        self, data: Union[pd.DataFrame, gpd.GeoDataFrame], **kwargs
    ) -> FieldTypeVerificationError:
        errors = []
        for column_data in self.fields_type_verification.columns:
            
            if column_data.mandatory:
                errors_mandatory = self.validate_mandatory(data[column_data.column], column_data.column)
                if errors_mandatory is not None:
                    errors.append(errors_mandatory)
        
        return errors
    
    def validate_inputs(self) -> None:
        if self.fields_type_verification is None or not isinstance(self.fields_type_verification, FieldTypeVerification):
            raise ValueError(f"❌ ")