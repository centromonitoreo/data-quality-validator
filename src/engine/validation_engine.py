from data_access.interface import IDataReader
from error_handlers.interface import IErrorHandler
from rule_access.interface import IRulesReader
from rule_access.imp.database_reader.database_rules_reader import RuleAccessDataBase
from error_handlers.imp.delete_strategy.delete_strategy import DeleteErrorHandler
from data_access.imp.gdb_reader.gdb_reader import GdbReader
from data_access.imp.postgres_reader.postgres_reader import PostgresReader
from validators.imp.duplicate_validator.duplicate_validator import DuplicatesIdentifyValidator
from validators.imp.field_validator.field_validator import FieldTypeVerificationValidator
from validators.imp.natural_limits_validator.natural_limits_validator import NaturalLimitsValidator
from validators.imp.mandatory_validator.mandatory_validator import MandatoryVerificationValidator
from validators.imp.relationship_validator.relationship_validator import RelationshipDataValidator
from enum import Enum
from typing import Dict


class RulesReaderEnum(Enum):
    database_rule_reader = RuleAccessDataBase


class ErrorHandlerEnum(Enum):
    delete_strategy = DeleteErrorHandler


class ReaderDataEnum(Enum):
    gdb_reader = GdbReader
    postgres_reader = PostgresReader


class ValidationEngine:
    def __init__(
        self,
        thematic: str,
        reader: str,
        rules_reader: str,
        error_handler: str,
        **kwargs,
    ):

        self.reader: IDataReader = ReaderDataEnum[reader].value(**kwargs)
        self.thematic: str = thematic
        self.rules: IRulesReader = RulesReaderEnum[rules_reader].value(thematic)
        self.error_handler: IErrorHandler  = ErrorHandlerEnum[error_handler].value
        self.error_handler_name:str = error_handler
        self.data: Dict = None
        self.kwargs = kwargs
        self.reader.validate_inputs()

    def run(self):
        self.data = self.rules.get_data(self.reader)
                
        # table validations
        print("---------------TABLAS------------------------------")
        print({table:len(data) for table, data in self.data.items()})
        for table_name in self.data.keys():
            # self.kwargs['table_name'] = table_name
            self.kwargs['table_name'] = "MuestreoHidrobioTB"
            table_name = "MuestreoHidrobioTB"
            for validator in self.rules.get_validators(table_name, self.error_handler_name):
                print(f"----Evaluating {validator.__name__}-{table_name}-----------")
                kwargs_validator = self.rules.get_validate_args(validator, **self.kwargs)
                validator_inst = validator(**kwargs_validator)
                validator_inst.validate_inputs()
                validator_inst.validate(self.data[table_name].copy())
                errors = validator_inst.error_handler_adapter(self.error_handler, self.kwargs['table_name'])
                error_handler = self.error_handler(**errors)
                error_handler.validate_inputs()
                self.data[table_name] = error_handler.handle_table_error(self.data[table_name],self.kwargs['table_name'])
                # print({table:len(data) for table, data in self.data.items()})

        # thematic validations
        print("---------------Tematico------------------------------")
        print({table:len(data) for table, data in self.data.items()})
        for validator_thematic in self.rules.get_validators_thematic():
            print(f"----Evaluating {validator_thematic.__name__}----")
            kwargs_validator = self.rules.get_validate_args(
                validator_thematic, **self.kwargs
            )
            validator_inst = validator_thematic(**kwargs_validator)
            validator_inst.validate_inputs()
            validator_inst.validate(self.data)
            errors = validator_inst.error_handler_adapter(self.error_handler, self.kwargs['table_name'])
            error_handler = self.error_handler(**errors)
            error_handler.validate_inputs()
            self.data = error_handler.handle_thematic_error(self.data.copy())
            print({table:len(data) for table, data in self.data.items()})
        return self.data
