from pydantic import BaseModel, Field
from typing import List, Optional


class GenerateIdInput(BaseModel):
    father_table: str
    buffer_distance: int
    child_tables: List[str]
    id_gdb: str
    id_anla: str
    acronym: str
    cols_validate: Optional[List[str]] = Field(default_factory=list)
    is_point: bool

