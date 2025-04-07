from pydantic import BaseModel
from enum import Enum
from typing import Union, List


class DistributionParamType(Enum):
    horizontal = "Horizontal"
    vertical = "Vertical"

class LimitPara(BaseModel):
    param_name:Union[str, int]
    limit_max:float
    limit_min:float

class HorizontalLimit(BaseModel):
    limits: List[LimitPara]

class VerticalLimits(BaseModel):
    column_name_param: str
    column_name_value: str
    limits: List[LimitPara]

class NaturalLimitsInput(BaseModel):
    distribution_param_type: DistributionParamType
    limits_data: Union[HorizontalLimit, VerticalLimits]

class VerticalError(BaseModel):
    param: str
    index: int
    value: float
    limit_max:float
    limit_min:float

class VerticalErrors(BaseModel):
    column_name: str
    errors: List[VerticalError]

class HorizontalError(BaseModel):
    index: int
    value: float
    limit_max:float
    limit_min:float

class HorizontalErrors(BaseModel):
    column_param: str
    errors: List[HorizontalError]

class NaturalLimitsErros(BaseModel):
    distribution_param_type: DistributionParamType
    errors: Union[List[HorizontalErrors], List[VerticalErrors]]
    