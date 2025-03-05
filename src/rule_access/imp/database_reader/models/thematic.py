import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from database.config import Base
from sqlalchemy.orm import relationship

class Thematic(Base):
    __tablename__ = 'thematic'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    nombre_grupo = Column(String, nullable=False)
    tables = relationship('Table', back_populates='thematic')