from rule_access.imp.database_reader.config import Base, engine
from sqlalchemy import Column, ForeignKey, Enum, String, ARRAY
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
    left_table_id = Column(String, nullable=False)
    right_table_id = Column(String, nullable=False)
    primary_key_column = Column(ARRAY(String), nullable=False)
    foreign_key_column = Column(ARRAY(String), nullable=False)
    relationship = Column(Enum(RelatioshipEnum, name="relationship_enum"), nullable=False)

Base.metadata.create_all(bind=engine)