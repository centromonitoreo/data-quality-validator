from data_access.interface import IDataReader
from error_handlers.interface import IErrorHandler
from rule_access.interface import IRulesReader
from rule_access.imp.database_reader.database_rules_reader import RuleAccessDataBase
from error_handlers.imp.delete_strategy.delete_strategy import DeleteErrorHandler
from data_access.imp.gdb_reader.gdb_reader import GdbReader
from data_access.imp.postgres_reader.postgres_reader import PostgresReader
from validators.imp.taxonomy.taxonomy_validator import TaxonomyValidator
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

        if not self._has_data():
            print(
                f"No se encontró información para el temático '{self.thematic}'. "
                "Se omite la validación."
            )
            return self.data

        # table validations
        print("---------------TABLAS------------------------------")
        print({table:len(data) for table, data in self.data.items()})
        for table_name in self.data.keys():
            self.kwargs['table_name'] = table_name
            for validator in self.rules.get_validators(table_name, self.error_handler_name):
                print(f"----Evaluating {validator.__name__}-{table_name}-----------")
                kwargs_validator = self.rules.get_validate_args(validator, **self.kwargs)
                validator_inst = validator(**kwargs_validator)
                validator_inst.validate_inputs()
                table_data = self.data[table_name].copy()
                validator_inst.validate(table_data)
                if validator == TaxonomyValidator:
                    self.data[table_name] = validator_inst.taxonomy_data
                else:
                    errors = validator_inst.error_handler_adapter(self.error_handler, self.kwargs['table_name'])
                    error_handler = self.error_handler(**errors)
                    error_handler.validate_inputs()
                    self.data[table_name] = error_handler.handle_table_error(table_data,self.kwargs['table_name'])

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

    def _has_data(self) -> bool:
        if not self.data:
            return False

        for table_data in self.data.values():
            if table_data is None:
                continue
            if hasattr(table_data, "empty"):
                if not table_data.empty:
                    return True
            else:
                try:
                    if len(table_data) > 0:
                        return True
                except TypeError:
                    continue
        return False
