from rule_access.interface import IRulesReader
from validators.imp.relationship_validator.relationship_validator import RelationshipDataValidator
from validators.imp.relationship_validator.schemas.shemas import RelationshipData
from validators.interface import IValidator
from data_access.interface import IDataReader
from rule_access.imp.database_reader.services.implements.default_tables_services import TableServiceImpl
from rule_access.imp.database_reader.services.implements.default_validations_service import ValidationServiceImp
from rule_access.imp.database_reader.services.implements.default_relationship_service import RelationshipServiceImp
from validators.imp.relationship_validator.relationship_validator import RelationshipDataValidator
from typing import List, Dict, Union
import geopandas as gpd
import pandas as pd
from enum import Enum


class ValidationsEnum(Enum):
    relationship = RelationshipDataValidator

class RuleAccessDataBase(IRulesReader):

    def get_validators(self, table_name:str) -> List[IValidator]:
        validations =  ValidationServiceImp().get_validations_by_table(table_name)
        return [ValidationsEnum[validation.name].value for validation in validations]

    def get_data(self, data_reader: IDataReader) -> Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]:
        tables = TableServiceImpl().get_tables_by_thematic(self.thematic)
        dict_result = {}
        for table in tables:
            dict_result[table.name] = data_reader.read_data(table.name)
        return dict_result
    

    def get_validate_args(self, validator: IValidator, **kwargs):
        if isinstance(validator, RelationshipDataValidator):
            return self.get_relationship_args(**kwargs)
        raise("Validator Method is not suscribed")


    def get_relationship_args(self, **kwargs) -> List[RelationshipData]:
        table_name = kwargs['table_name']
        validations = RelationshipServiceImp().get_relationship_by_table(table_name)
        relationship_data =  [
            RelationshipData(
                left_table= validation.left_table.name,
                rigth_table = validation.right_table.name,
                type_relation= validation.relationship
            )

            for validation in validations
        ]
        return {"relationship_data": relationship_data}