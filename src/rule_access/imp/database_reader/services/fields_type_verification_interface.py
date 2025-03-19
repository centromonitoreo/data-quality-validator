from abc import ABC, abstractmethod
from rule_access.imp.database_reader.models.field_type_verification import FieldTypeVerificationTable
from typing import List

class FieldTypeService(ABC):

    @abstractmethod
    def get_field_verification_by_table(self, table_name) -> List[FieldTypeVerificationTable]:
        pass