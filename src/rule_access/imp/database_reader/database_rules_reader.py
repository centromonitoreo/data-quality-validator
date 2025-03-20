from rule_access.interface import IRulesReader
from validators.imp.relationship_validator.relationship_validator import (
    RelationshipDataValidator,
)
from validators.imp.relationship_validator.schemas.schemas import RelationShipInput
from validators.interface import IValidator
from data_access.interface import IDataReader
from rule_access.imp.database_reader.services.implements.default_tables_services import (
    TableServiceImpl,
)
from rule_access.imp.database_reader.services.implements.default_validations_service import (
    ValidationServiceImp,
)
from rule_access.imp.database_reader.services.implements.default_relationship_service import (
    RelationshipServiceImp,
)
from rule_access.imp.database_reader.services.implements.default_fields_type_verification_service import FieldTypeServiceImp
from rule_access.imp.database_reader.services.implements.default_duplicated_self_table_service import (
    DuplicateSelfTableServiceImp,
)
from rule_access.imp.database_reader.services.implements.default_domains_service import DomainTableServiceImp
from rule_access.imp.database_reader.services.implements.default_validation_thematic_service import (
    ValidationThematicServiceImp,
)

from validators.imp.duplicate_validator.schemas.schemas import DuplicatesIdentifyInput
from validators.imp.field_validator.schemas.schemas import FieldTypeVerification, FieldTypeColumn
from validators.imp.duplicate_validator.duplicate_validator import (
    DuplicatesIdentifyValidator,
)
from validators.imp.field_validator.field_validator import FieldTypeVerificationValidator


from typing import List, Dict, Union
import geopandas as gpd
import pandas as pd
from enum import Enum


class ValidationsEnum(Enum):
    relationship = RelationshipDataValidator
    duplicated_self_table =  DuplicatesIdentifyValidator

class RuleAccessDataBase(IRulesReader):

    def get_validators(self, table_name: str, error_handler_strategy_name:str) -> List[IValidator]:
        validations = ValidationServiceImp().get_validations_by_table(table_name, error_handler_strategy_name)
        return [ValidationsEnum[validation.name].value for validation in validations]

    def get_validators_thematic(self):
        validations = ValidationThematicServiceImp().get_validations_by_thematic(
            self.thematic
        )
        return [ValidationsEnum[validation.name].value for validation in validations]

    def get_data(
        self, data_reader: IDataReader
    ) -> Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]:
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
        if validator == FieldTypeVerificationValidator:
            return self.get_field_type_verification(**kwargs)
        raise("Validator Method is not suscribed")


    def get_duplicater_self_table(self, **kwargs) -> DuplicatesIdentifyInput:
        table_name = kwargs['table_name']
        duplicate_self_table = DuplicateSelfTableServiceImp().get_duplicated_self_table_by_table_name(table_name)
        return {"duplicates_identify_input": DuplicatesIdentifyInput(
            columns= duplicate_self_table.columns
        )}
    

    def get_values_domain(self, domain_name) -> List[str]:
        return {domain.domain_id: domain.description for domain in DomainTableServiceImp().get_domains_by_domain_name(domain_name)}
    

    def get_field_type_verification(self, **kwargs) -> FieldTypeVerification:
        table_name = kwargs['table_name']
        field_type_table = FieldTypeServiceImp().get_field_verification_by_table(table_name)


        fields_type_verification = FieldTypeVerification(columns=[
                                    FieldTypeColumn(
                                        column= field_type_column.field,
                                        type= field_type_column.data_type,
                                        mandatory= field_type_column.obligatory == "Mandatory",
                                        domain_values= None if field_type_column.domain_name is None else self.get_values_domain(field_type_column.domain_name)
                                    )
                                    for field_type_column in field_type_table
                                ])
          
        return {"fields_type_verification": fields_type_verification}
    

    def get_relationship_args(self, **kwargs) -> Dict[str, List[RelationShipInput]]:

        validation_self_table = RelationshipServiceImp().get_relationship_by_thematic(
            self.thematic
        )
        relationship_data = [
            RelationShipInput(
                left_table=TableServiceImpl()
                .get_table_by_id(validation.left_table_id)
                .name,
                left_key=validation.primary_key_column,
                right_table=TableServiceImpl()
                .get_table_by_id(validation.right_table_id)
                .name,
                right_key=validation.foreign_key_column,
                type_relation=validation.relationship.value,
            )
            for validation in validation_self_table
        ]
        return {"relationship_data": relationship_data}
