from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.natural_limits_values import NaturalLimitsValuesTable
from typing import List

class NaturalLimitsValuesService(ABC):

    @abstractmethod
    def get_natural_limits_values_table_by_table_name(self, id_orientation) -> List[NaturalLimitsValuesTable]:
        pass