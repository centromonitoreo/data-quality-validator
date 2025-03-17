from validators.interface import IValidator
from validators.imp.field_validator.schemas.schemas import FieldTypeVerification
from validators.imp.field_validator.schemas.schemas import FieldTypeVerificationError
import geopandas as gpd
from typing import Union
import pandas as pd


class FieldTypeVerificationValidator(IValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'fields_type_verification'):
            self.fields_type_verification = None

    def validate(
        self, data: Union[pd.DataFrame, gpd.GeoDataFrame], **kwargs
    ) -> FieldTypeVerificationError:
        #TODO implementar proceso de verificacion del tipo de campo
        pass


    def validate_inputs(self) -> None:
        if self.fields_type_verification is None or not isinstance(self.fields_type_verification, FieldTypeVerification):
            raise ValueError(f"❌ ")