from pydantic import BaseModel
from typing import List
class DuplicatesIdentifyInput(BaseModel):
    columns : List[str]