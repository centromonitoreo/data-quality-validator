from pydantic import BaseModel
from typing import List, Union
from enum import Enum


class FieldTypeColumn(BaseModel):    
    column : str    
    type : str    
    domain_values: List[str]
    
    
class FieldTypeVerification(BaseModel):    
    columns : List[FieldTypeColumn]
    
    
class DataType(Enum):
    string = "string"
    datetime = "datetime"
    integer = "integer"
    double = "double"
    
    
class ErrorType(Enum):
    type_error = "type_error"
    domain_error = "domain_error"
    mandatory_error = "mandatory_error" # Por esto es el None
    
    
class TypeErrorData(BaseModel):
    data_type: DataType
    value: Union[str, int, float]
    
    
class DomainErrorData(BaseModel):
    domain_name: str 
    value: str
    valid_values: List[str]
    
      
       
class FieldTypeVerificationError(BaseModel):    
    column : str    
    row : int    
    error_type: ErrorType
    error_data: Union[TypeErrorData, DomainErrorData, None]

