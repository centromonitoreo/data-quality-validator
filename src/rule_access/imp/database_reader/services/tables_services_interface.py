from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.tables import Table
from typing import List
import uuid
class TableService(ABC):

    @abstractmethod
    def get_tables_by_thematic(self, thematic) -> List[Table]:
        pass


    @abstractmethod
    def get_table_by_id(self, table_id: uuid.uuid4) -> Table:
        pass
    