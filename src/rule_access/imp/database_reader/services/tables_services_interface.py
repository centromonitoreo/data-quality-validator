from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.tables import Table
from typing import List

class TableService(ABC):

    @abstractmethod
    def get_tables_by_thematic(self, thematic) -> List[Table]:
        pass

    