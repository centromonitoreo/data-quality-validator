from pydantic import BaseModel
from typing import List
class DuplicatesIdentifyInput(BaseModel):
    columns : List[str]

class DuplicatesIdentifyError(BaseModel):
    duplicate_index: List[int]
    duplicate_data: List[str]

class DuplicatesIndentifyErrors(BaseModel):
    list_errors: List[DuplicatesIdentifyError]