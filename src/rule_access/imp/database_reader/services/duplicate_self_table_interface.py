from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.duplicate_self_table import DuplicateSelfTable
from typing import List

class DuplicateSelfTableService(ABC):

    @abstractmethod
    def get_duplicated_self_table_by_table_name(self, table_name) -> DuplicateSelfTable:
        pass

    