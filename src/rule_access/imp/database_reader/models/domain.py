from rule_access.imp.database_reader.config import Base, engine
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship

#Esta es mi tabla de postgres que tiene las verificaiones de campos
class DomainTable(Base):
    __tablename__ = 'domain'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    domain_name = Column(String, nullable=False)
    domain_id = Column(String, nullable=False)
    description = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)