from pydantic import BaseModel
from typing import List, Union
from datetime import date
import numpy as np

class FieldTypeColumn(BaseModel):
    column : str
    type : str
    domain_values: List[str]


class FieldTypeVerification(BaseModel):
    columns : List[FieldTypeColumn]


# Salida
class FieldTypeVerificationError(BaseModel):
    column : str
    row : int
    error : str