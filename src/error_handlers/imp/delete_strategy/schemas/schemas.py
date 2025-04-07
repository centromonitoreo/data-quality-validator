from pydantic import BaseModel
from typing import List, Union


class DeleteRows(BaseModel):
    index: List[int]

class DeleteData(BaseModel):
    column: str
    index: List[int]

class DeleteTableErrors(BaseModel):
    table_name: str
    errors: Union[List[DeleteData], DeleteRows]

class DeleteErrorsInput(BaseModel):
    errors: List[DeleteTableErrors]
