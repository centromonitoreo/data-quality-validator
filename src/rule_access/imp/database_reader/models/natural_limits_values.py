import uuid
from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from rule_access.imp.database_reader.config import Base, engine


class NaturalLimitsValuesTable(Base):
    __tablename__ = "natural_limits_values"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    id_orientation = Column(UUID(as_uuid=True), ForeignKey('natural_limits_orientation_search.id'), nullable=False)
    parameter = Column(String, nullable=False)
    description = Column(String, nullable=False)
    lower_limit = Column(Float, nullable=True)
    upper_limit = Column(Float, nullable=True)
    natural_limits_orientation_search = relationship('NaturalLimitsOrientationSearchTable', back_populates='natural_limits_values')

    # @property
    # def table_name(self):
    #     return self.natural_limits_orientation_search.table.name if self.natural_limits_orientation_search else None


Base.metadata.create_all(bind=engine)