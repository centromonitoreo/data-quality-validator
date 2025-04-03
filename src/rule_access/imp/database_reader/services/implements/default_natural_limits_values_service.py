from rule_access.imp.database_reader.services.natural_limits_values_service_interface import NaturalLimitsValuesService
from rule_access.imp.database_reader.config import SessionManager
from rule_access.imp.database_reader.models.natural_limits_values import NaturalLimitsValuesTable
from rule_access.imp.database_reader.models.natural_limits_orientation_search import NaturalLimitsOrientationSearchTable

class NaturalLimitsValuesTableServiceImp(NaturalLimitsValuesService):

    def get_natural_limits_values_table_by_table_name(self, id_orientation) -> NaturalLimitsValuesTable:
        return SessionManager().get_session().query(NaturalLimitsValuesTable).join(NaturalLimitsOrientationSearchTable).filter(NaturalLimitsOrientationSearchTable.id==id_orientation).all()