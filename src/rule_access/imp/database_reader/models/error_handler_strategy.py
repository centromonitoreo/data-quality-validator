from rule_access.imp.database_reader.config import Base, engine
from sqlalchemy import Column, ForeignKey, Enum, String, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as EnumClass
from sqlalchemy.orm import relationship


class ErrorHandlerStrategy(Base):
    __tablename__ = 'error_handler_strategy'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    strategy_name = Column(String, nullable=False)
    validations = relationship('Validation', back_populates='error_handler_strategy')


Base.metadata.create_all(bind=engine)