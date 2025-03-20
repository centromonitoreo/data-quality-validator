from enum import Enum
from pydantic import BaseModel
from typing import Any, Dict, List, Tuple


class TypeRelation(Enum):
    many_to_one = "ManyToOne"
    one_to_many = "OneToMany"


class RelationShipInput(BaseModel):
    left_table: str
    left_key: List[str]
    right_table: str
    right_key: List[str]
    type_relation: str


class RelationshipError(BaseModel):
    key_columns: Tuple[str, ...]
    missing_keys: List[Any]


class RelationShipOutput(BaseModel):
    errors: Dict[str, List[RelationshipError]]
