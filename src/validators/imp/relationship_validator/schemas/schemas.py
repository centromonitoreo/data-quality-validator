from pydantic import BaseModel
from enum import Enum
from typing import Union
class TypeRelation(Enum):
    many_to_one = "ManyToOne"
    one_to_may = "OneToMany"


class RelationshipData(BaseModel):
    left_table: str
    rigth_table: str
    primary_key_column: Union[list, str]
    foreign_key_column: Union[list, str]
    type_relation: TypeRelation