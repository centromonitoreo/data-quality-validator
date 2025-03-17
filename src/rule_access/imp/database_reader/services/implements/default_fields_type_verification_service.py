from rule_access.imp.database_reader.services.fields_type_verification_interface import FieldTypeService
from rule_access.imp.database_reader.config import SessionManager
from rule_access.imp.database_reader.models.field_type_verification import FieldTypeVerificationTable
from rule_access.imp.database_reader.models.tables import Table
from typing import List

class FieldTypeServiceImp(FieldTypeService):

    def get_field_verification_by_table(self, table_name) -> List[FieldTypeVerificationTable]:
        return SessionManager().get_session().query(FieldTypeVerificationTable).join(Table).filter(Table.name==table_name).first()