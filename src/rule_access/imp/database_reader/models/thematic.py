import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from rule_access.imp.database_reader.config import Base, engine
from sqlalchemy.orm import relationship


class Thematic(Base):
    __tablename__ = "thematic"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    group_name = Column(String, nullable=False)
    tables = relationship("Table", back_populates="thematic")
    validations = relationship("ValidationThematic", back_populates="thematic")
    relationships = relationship("Relationship", back_populates="thematic")

    __table_args__ = {"extend_existing": True}


Base.metadata.create_all(bind=engine)
