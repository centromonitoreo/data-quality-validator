from pydantic import BaseModel
from typing import List, Union, Dict
from enum import Enum


class FieldTypeColumn(BaseModel):    
    column : str    
    type : str
    mandatory: bool
    domain_values: Union[Dict, None]
    
    
class FieldTypeVerification(BaseModel):    
    columns : List[FieldTypeColumn]
    
    
class DataType(Enum):
    string = "str"
    datetime = "datetime"
    integer = "int"
    float = "float" # float64
    
    
class ErrorType(Enum):
    type_error = "type_error"
    domain_error = "domain_error"
    mandatory_error = "mandatory_error" # Por esto es el None
    
    
class TypeErrorData(BaseModel):
    data_type: DataType
    index: int
    value: Union[str, int, float]
    
    
class DomainErrorData(BaseModel):
    value: str
    index: int
    valid_values: List[str]

class MandatoryErrorData(BaseModel):
    list_index: List[int]
    
       
class FieldTypeVerificationError(BaseModel):    
    column : str        
    error_type: ErrorType
    error_data: Union[List[TypeErrorData], List[DomainErrorData], MandatoryErrorData]

