from validators.interface import IValidator
from validators.imp.field_validator.schemas.schemas import FieldTypeVerification
from validators.imp.field_validator.schemas.schemas import FieldTypeVerificationError
from validators.imp.field_validator.schemas.schemas import TypeErrorData, DomainErrorData, ErrorType, MandatoryErrorData, DataType
import geopandas as gpd
from typing import Union, List
import pandas as pd
from rule_access.imp.database_reader.config import engine


class FieldTypeVerificationValidator(IValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'fields_type_verification'):
            self.fields_type_verification = None

    def validate_domain(self, values: pd.Series, domain_values, column_name) -> List[DomainErrorData]:
        data_errors = values[~values.dropna().astype(int).astype(str).isin(domain_values.keys())]

        if len(data_errors) == 0:
            return None

        return FieldTypeVerificationError(
            column=column_name,
            error_type=ErrorType.domain_error,
            error_data=[DomainErrorData(index= index, value=str(value), valid_values=list(domain_values.values())) for index, value in data_errors.items()]
        )
    
    
    def validate_mandatory(self, values: pd.Series, column_name) -> FieldTypeVerificationError:
        data_errors = values[values.isnull() | values.isna()]

        if len(data_errors) == 0:
            return None
        
        return FieldTypeVerificationError(
            column=column_name,
            error_type=ErrorType.mandatory_error,
            error_data=MandatoryErrorData(list_index=data_errors.index.tolist())
        )
        
    def validate_doubles(self, values: pd.Series) -> FieldTypeVerificationError:
        errors = []
        for index, value in values.dropna().items():
            try:
                float(value)
            except ValueError:
                errors.append(TypeErrorData(data_type=DataType.double, value=value))
        if errors:
            return errors


    def validate_datetime(self, values: pd.Series) -> FieldTypeVerificationError:
        errors = []
        for index, value in values.items():
            try:
                pd.to_datetime(value)
            except ValueError:
                errors.append(TypeErrorData(data_type=DataType.datetime, value=value))
        
        if errors:
            return errors

    def validate_type(self, values:pd.Series, data_type: str, column_name) -> FieldTypeVerificationError:
        error = None
        data_type = DataType(data_type)
        if data_type == DataType.double:
            error = self.validate_doubles(values)
        elif data_type == DataType.datetime:
            error = self.validate_datetime(values)
        if error is None:
            return None
        return FieldTypeVerificationError(
                column=column_name,
                error_type=ErrorType.type_error,
                error_data=error
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

            if len(column_data.domain_values) > 0:
                errors_domain = self.validate_domain(data[column_data.column], column_data.domain_values, column_data.column)
                if errors_domain is not None:
                    errors.append(errors_domain)
                    continue

            errors_type = self.validate_type(data[column_data.column], column_data.type, column_data.column)
            if errors_type is not None:
                errors.append(errors_type)

        return errors


    def validate_inputs(self) -> None:
        if self.fields_type_verification is None or not isinstance(self.fields_type_verification, FieldTypeVerification):
            raise ValueError(f"❌ ")