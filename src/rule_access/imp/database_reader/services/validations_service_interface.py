from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.validation import Validation
from typing import List

class ValidationService(ABC):

    @abstractmethod
    def get_validations_by_table(self, table_name: str) -> List[Validation]:
        pass
