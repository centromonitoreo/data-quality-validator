from rule_access.interface import IRulesReader
from validators.imp.relationship_validator.schemas.schemas import RelationShipInput
from validators.imp.relationship_validator.relationship_validator import (
    RelationshipDataValidator,
)

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
from rule_access.imp.database_reader.services.implements.default_natural_limits_orientation_service import NaturalLimitsOrientationTableServiceImp
from validators.imp.duplicate_validator.schemas.schemas import DuplicatesIdentifyInput
from validators.imp.field_validator.schemas.schemas import FieldTypeVerification, FieldTypeColumn
from validators.imp.duplicate_validator.duplicate_validator import (
    DuplicatesIdentifyValidator,
)
from validators.imp.field_validator.field_validator import FieldTypeVerificationValidator
from validators.imp.natural_limits_validator.natural_limits_validator import NaturalLimitsValidator
from validators.imp.natural_limits_validator.schemas.schemas import DistributionParamType, LimitPara, HorizontalLimit, VerticalLimits, NaturalLimitsInput
from rule_access.imp.database_reader.preprocess_data.generate_ids.schemas.schemas import GenerateIdInput
from rule_access.imp.database_reader.services.implements.default_generate_ids_service import (
    GenerateIdServiceImp,
)
from rule_access.imp.database_reader.preprocess_data.clean_ids.clean_invalid_ids import process_invalid_ids
from rule_access.imp.database_reader.preprocess_data.generate_ids.generate_ids import IdGenerator
from validators.imp.mandatory_validator.mandatory_validator import MandatoryVerificationValidator

from typing import List, Dict, Union, Any
import geopandas as gpd
import pandas as pd
from enum import Enum
import numpy as np

def load_tables_data(data_reader: IDataReader, thematic: str) -> dict:
        tables = TableServiceImpl().get_tables_by_thematic(thematic)
        data_dict = {table.name: data_reader.read_data(table.name).drop_duplicates() for table in tables}
        return data_dict
    
def prepare_generate_id_data(thematic: str) -> List[GenerateIdInput]:
    instructions = GenerateIdServiceImp().get_generate_id_by_thematic(thematic)
    generate_id_data = [
        GenerateIdInput(
            father_table=instruction.father_name,
            buffer_distance=instruction.buffer_distance,
            child_tables=instruction.children_names,
            id_gdb=instruction.id_gdb,
            id_anla=instruction.id_anla,
            acronym=instruction.acronym,
            cols_validate=instruction.cols_validate,
            is_point=instruction.is_point,
        )
        for instruction in instructions
    ]
    return generate_id_data

def generate_ids(data_dict: Dict[str, Any], generate_id_data: List[GenerateIdInput]) -> Dict[str, Any]:
    id_generator = IdGenerator(generate_id_data=generate_id_data)
    data_with_ids = id_generator.validate(data_dict)
    return data_with_ids

class ValidationsEnum(Enum):
    relationship = RelationshipDataValidator
    duplicated_self_table =  DuplicatesIdentifyValidator
    fields_type_verification = FieldTypeVerificationValidator    
    natural_limits = NaturalLimitsValidator
    mandatory_verification = MandatoryVerificationValidator

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
        
        data_dict = load_tables_data(data_reader, self.thematic)
        id_instructions = prepare_generate_id_data(self.thematic)
        data_with_ids = generate_ids(data_dict, id_instructions)
        dict_result = process_invalid_ids(data_with_ids)
        
        return dict_result

    def get_validate_args(self, validator: IValidator, **kwargs):
        if validator == RelationshipDataValidator:
            return self.get_relationship_args(**kwargs)
        if validator == DuplicatesIdentifyValidator:
            return self.get_duplicater_self_table(**kwargs)
        if validator == FieldTypeVerificationValidator:
            return self.get_field_type_verification(**kwargs)
        if validator == MandatoryVerificationValidator:
            return self.get_field_type_verification(**kwargs)
        if validator == NaturalLimitsValidator:
            return self.get_natural_limits_values(**kwargs)
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
    
    
    def get_natural_limits_values(self, **kwargs) -> NaturalLimitsInput:
        table_name = kwargs['table_name']
        natural_limits_orientation_search = NaturalLimitsOrientationTableServiceImp().get_natural_limits_orientation_table_by_table_name(table_name)
        natural_limits_values_search = natural_limits_orientation_search.natural_limits_values
        distribution_param_type = natural_limits_orientation_search.orientation
        
        limit = []

        for parameter in natural_limits_values_search:
            limit.append(
                LimitPara(
                    param_name=parameter.parameter,
                    limit_min=parameter.lower_limit if parameter.lower_limit is not None else np.nan,
                    limit_max=parameter.upper_limit if parameter.upper_limit is not None else np.nan,
                )
            )
            if DistributionParamType.horizontal.value == distribution_param_type:
                horizontal_limits= HorizontalLimit(
                        limits=limit,
                    )
            elif DistributionParamType.vertical.value == distribution_param_type:
                vertical_limits=VerticalLimits(
                        column_name_param=natural_limits_orientation_search.search_column[0],
                        column_name_value=natural_limits_orientation_search.search_column[1],
                        limits=limit,
                    )

            inputs_natural_limits = NaturalLimitsInput(
                distribution_param_type=distribution_param_type,
                limits_data=horizontal_limits if DistributionParamType.horizontal.value == distribution_param_type else vertical_limits,
            )

        return {"natural_limits": inputs_natural_limits} 