from rule_access.imp.database_reader.services.natural_limits_orientation_services_interface import NaturalLimitsOrientationService
from rule_access.imp.database_reader.config import SessionManager
from rule_access.imp.database_reader.models.natural_limits_orientation_search import NaturalLimitsOrientationSearchTable
from rule_access.imp.database_reader.models.tables import Table
from typing import List

class NaturalLimitsOrientationTableServiceImp(NaturalLimitsOrientationService):

    def get_natural_limits_orientation_table_by_table_name(self, table_name: str) -> List[NaturalLimitsOrientationSearchTable]:
        return SessionManager().get_session().query(NaturalLimitsOrientationSearchTable).join(Table).filter(Table.name==table_name).first()