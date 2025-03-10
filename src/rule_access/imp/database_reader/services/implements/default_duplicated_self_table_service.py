from rule_access.imp.database_reader.services.duplicate_self_table_interface import DuplicateSelfTableService
from rule_access.imp.database_reader.config import SessionManager
from rule_access.imp.database_reader.models.duplicate_self_table import DuplicateSelfTable
from rule_access.imp.database_reader.models.tables import Table

class DuplicateSelfTableServiceImp(DuplicateSelfTableService):

    def get_duplicated_self_table_by_table_name(self, table_name) -> DuplicateSelfTable:
        return SessionManager().get_session().query(DuplicateSelfTable).join(Table).filter(Table.name==table_name).first()