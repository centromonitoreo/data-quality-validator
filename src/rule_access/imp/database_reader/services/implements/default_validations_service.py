from rule_access.imp.database_reader.services.validations_service_interface import ValidationService
from rule_access.imp.database_reader.models.validation import Validation
from rule_access.imp.database_reader.models.tables import Table
from rule_access.imp.database_reader.config import SessionManager
from typing import List

class ValidationServiceImp(ValidationService):

    def get_validations_by_table(self, table_name) -> List[Validation] :
        return SessionManager().get_session().query(Validation).join(Table).filter(Table.name == table_name).all()

