from rule_access.imp.database_reader.config import Base
from sqlalchemy import Column, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as EnumClass
from sqlalchemy.orm import relationship as relationship_sql

class RelatioshipEnum(EnumClass):
    many_to_one = "ManyToOne"
    one_to_many = "OneToMany"
    many_to_many = "ManyToMany"


class Relationship(Base):
    __tablename__ = 'relationship'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    left_table_id =  Column(UUID(as_uuid=True), ForeignKey('table.id'), nullable=False)
    right_table_id =  Column(UUID(as_uuid=True), ForeignKey('table.id'), nullable=False)
    relationship = Column(Enum(RelatioshipEnum), nullable=False)
    left_table = relationship_sql('Table', foreign_keys=[left_table_id])
    right_table = relationship_sql('Table', foreign_keys=[right_table_id])


