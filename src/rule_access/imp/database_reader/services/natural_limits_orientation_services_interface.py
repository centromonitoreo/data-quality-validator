from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.natural_limits_orientation_search import NaturalLimitsOrientationSearchTable
from typing import List

class NaturalLimitsOrientationService(ABC):

    @abstractmethod
    def get_natural_limits_orientation_table_by_table_name(self, table_name) -> NaturalLimitsOrientationSearchTable:
        pass