from pydantic import BaseModel
from typing import List, Dict
class DuplicatesIdentifyInput(BaseModel):
    columns : List[str]

class DuplicatesIdentifyError(BaseModel):
    duplicate_index: List[int]
    duplicate_data: Dict

class DuplicatesIdentifyErrors(BaseModel):
    list_errors: List[DuplicatesIdentifyError]