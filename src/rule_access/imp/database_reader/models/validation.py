from rule_access.imp.database_reader.config import Base, engine
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

class Validation(Base):
    __tablename__='validation'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    table_id = Column(UUID(as_uuid=True), ForeignKey('table.id'), nullable=False)
    error_handler_strategy_id = Column(UUID(as_uuid=True), ForeignKey('error_handler_strategy.id'), nullable=False)
    name = Column(String, nullable=False)
    table = relationship('Table', back_populates='validations')
    error_handler_strategy = relationship('ErrorHandlerStrategy', back_populates='validations')


Base.metadata.create_all(bind=engine)