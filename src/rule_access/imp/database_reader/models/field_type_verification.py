from rule_access.imp.database_reader.config import Base, engine
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship


class FieldTypeVerificationTable(Base):
    __tablename__ = 'field_type_verification'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    table_id = Column(UUID(as_uuid=True), ForeignKey('table.id'), nullable=False)
    field = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    # homologation = Column(String, nullable=False)
    domain_id = Column(UUID(as_uuid=True), ForeignKey('domain.id'), nullable=False)
    obligatory = Column(String, nullable=False)
    domains = relationship('DomainTable')
    #TODO colocar un ENUM para data type

Base.metadata.create_all(bind=engine)