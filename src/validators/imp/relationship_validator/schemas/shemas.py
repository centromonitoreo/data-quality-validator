from pydantic import BaseModel
from enum import Enum

class TypeRelation(Enum):
    many_to_one = "ManyToOne"
    one_to_may = "OneToMany"


class RelationshipData(BaseModel):
    left_table: str
    rigth_table: str
    type_relation: TypeRelation