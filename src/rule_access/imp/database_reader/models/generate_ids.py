from rule_access.imp.database_reader.config import Base, engine
from sqlalchemy import Column, ForeignKey, String, ARRAY, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship as relationship_sql


class GenerateId(Base):
    __tablename__ = "generate_id"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    father_name = Column(String, nullable=False)
    buffer_distance = Column(Integer, nullable=False)
    children_names = Column(ARRAY(String), nullable=False)
    id_gdb = Column(String, nullable=False)
    id_anla = Column(String, nullable=False)
    acronym = Column(String, nullable=False)
    cols_validate = Column(ARRAY(String), nullable=True, default=list)
    is_point = Column(Boolean, nullable=False)
    thematic_id = Column(UUID(as_uuid=True), ForeignKey("thematic.id"), nullable=False)
    thematic = relationship_sql("Thematic", back_populates="generate_ids")


Base.metadata.create_all(bind=engine)
