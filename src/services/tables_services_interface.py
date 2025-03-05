from abc import ABC, abstractmethod
from database.models.tables import Table
from typing import List

class TableService(ABC):

    @abstractmethod
    def get_tables_by_thematic(self) -> List[Table]:
        pass

    