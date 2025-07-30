from rule_access.imp.database_reader.config import Base, engine
from sqlalchemy import Column, ForeignKey, Enum, String, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as EnumClass
from sqlalchemy.orm import relationship as relationship_sql
from sqlalchemy import Column, String, ARRAY, Enum as SAEnum


class RelationshipEnum(EnumClass):
    ONE_TO_ONE = "ONE_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_ONE = "MANY_TO_ONE"
    MANY_TO_MANY = "MANY_TO_MANY"


class Relationship(Base):
    __tablename__ = "relationship"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    left_table_id = Column(UUID(as_uuid=True), nullable=False)
    right_table_id = Column(UUID(as_uuid=True), nullable=False)
    primary_key_column = Column(ARRAY(String), nullable=False)
    foreign_key_column = Column(ARRAY(String), nullable=False)
    thematic_id = Column(UUID(as_uuid=True), ForeignKey("thematic.id"), nullable=False)
    thematic = relationship_sql("Thematic", back_populates="relationships")
    relationship = Column(
        SAEnum(RelationshipEnum, name="relationship_enum"), nullable=False
    )


Base.metadata.create_all(bind=engine)
