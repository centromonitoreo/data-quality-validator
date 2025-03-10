from rule_access.interface import IRulesReader
from validators.imp.relationship_validator.relationship_validator import RelationshipDataValidator
from validators.imp.relationship_validator.schemas.shemas import RelationshipData
from validators.interface import IValidator
from data_access.interface import IDataReader
from rule_access.imp.database_reader.services.implements.default_tables_services import TableServiceImpl
from rule_access.imp.database_reader.services.implements.default_validations_service import ValidationServiceImp
from rule_access.imp.database_reader.services.implements.default_relationship_service import RelationshipServiceImp
from rule_access.imp.database_reader.services.implements.default_duplicated_self_table_service import DuplicateSelfTableServiceImp
from validators.imp.relationship_validator.relationship_validator import RelationshipDataValidator
from validators.imp.duplicate_validator.schemas.schemas import DuplicatesIdentifyInput
from validators.imp.duplicate_validator.duplicate_validator import DuplicatesIdentifyValidator
from typing import List, Dict, Union
import geopandas as gpd
import pandas as pd
from enum import Enum


class ValidationsEnum(Enum):
    relationship = RelationshipDataValidator
    duplicated_self_table =  DuplicatesIdentifyValidator

class RuleAccessDataBase(IRulesReader):

    def get_validators(self, table_name:str, error_handler_strategy_name:str) -> List[IValidator]:
        validations =  ValidationServiceImp().get_validations_by_table(table_name, error_handler_strategy_name)
        return [ValidationsEnum[validation.name].value for validation in validations]

    def get_data(self, data_reader: IDataReader) -> Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]:
        tables = TableServiceImpl().get_tables_by_thematic(self.thematic)
        dict_result = {}
        for table in tables:
            dict_result[table.name] = data_reader.read_data(table.name)
        return dict_result
    

    def get_validate_args(self, validator: IValidator, **kwargs):
        if validator == RelationshipDataValidator:
            return self.get_relationship_args(**kwargs)
        if validator == DuplicatesIdentifyValidator:
            return self.get_duplicater_self_table(**kwargs)
        raise("Validator Method is not suscribed")


    def get_duplicater_self_table(self, **kwargs) -> DuplicatesIdentifyInput:
        table_name = kwargs['table_name']
        duplicate_self_table = DuplicateSelfTableServiceImp().get_duplicated_self_table_by_table_name(table_name)
        return {"duplicates_identify_input": DuplicatesIdentifyInput(
            columns= duplicate_self_table.columns
        )}


    def get_relationship_args(self, **kwargs) -> Dict[str, List[RelationshipData]]:
        table_name = kwargs['table_name']
        validations = RelationshipServiceImp().get_relationship_by_table(table_name)
        relationship_data =  [
            RelationshipData(
                left_table= TableServiceImpl().get_table_by_id(validation.left_table_id).name,
                rigth_table = TableServiceImpl().get_table_by_id(validation.right_table_id).name,
                type_relation= validation.relationship.value,
                primary_key_column = validation.primary_key_column,
                foreign_key_column = validation.foreign_key_column
            )

            for validation in validations
        ]
        return {"relationship_data": relationship_data}