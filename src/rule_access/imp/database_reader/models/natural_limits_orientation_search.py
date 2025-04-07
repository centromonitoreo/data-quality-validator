import uuid
from sqlalchemy import Column, String, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from rule_access.imp.database_reader.config import Base, engine


class NaturalLimitsOrientationSearchTable(Base):
    __tablename__ = "natural_limits_orientation_search"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    table_id = Column(UUID(as_uuid=True), ForeignKey('table.id'), nullable=False)
    orientation = Column(String, nullable=False)
    search_column = Column(ARRAY(String), nullable=False)
    natural_limits_values = relationship('NaturalLimitsValuesTable', back_populates='natural_limits_orientation_search')
    table = relationship('Table', back_populates='natural_limits_orientation_search')

    # @property
    # def table_name(self):
    #     return self.table.name if self.table else None


Base.metadata.create_all(bind=engine)