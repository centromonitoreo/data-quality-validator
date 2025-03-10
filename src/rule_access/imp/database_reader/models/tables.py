import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from rule_access.imp.database_reader.config import Base, engine

class Table(Base):
    __tablename__ = 'table'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, nullable=False)
    thematic_id = Column(UUID(as_uuid=True), ForeignKey('thematic.id'), nullable=False)
    thematic = relationship('Thematic', back_populates='tables')
    validations = relationship('Validation', back_populates='table')
    duplicate_self_table = relationship('DuplicateSelfTable', back_populates='table')

Base.metadata.create_all(bind=engine)