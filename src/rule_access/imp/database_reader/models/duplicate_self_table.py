from rule_access.imp.database_reader.config import Base, engine
from sqlalchemy import Column, ForeignKey, Enum, String, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as EnumClass
from sqlalchemy.orm import relationship


class DuplicateSelfTable(Base):
    __tablename__ = 'duplicate_self_table'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    columns = Column(ARRAY(String), nullable=False)
    table_id = Column(UUID(as_uuid=True), ForeignKey('table.id'), nullable=False)
    table = relationship('Table', back_populates='duplicate_self_table')

Base.metadata.create_all(bind=engine)