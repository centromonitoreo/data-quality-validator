from rule_access.imp.database_reader.config import Base, engine
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class ValidationThematic(Base):
    __tablename__ = "validation_thematic"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    thematic_id = Column(UUID(as_uuid=True), ForeignKey("thematic.id"), nullable=False)
    name = Column(String, nullable=False)
    thematic = relationship("Thematic", back_populates="validations")


Base.metadata.create_all(bind=engine)
