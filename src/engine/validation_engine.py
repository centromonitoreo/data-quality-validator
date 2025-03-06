
from data_access.interface import IDataReader
from error_handlers.interface import IErrorHandler
from rule_access.interface import IRulesReader
from rule_access.imp.database_reader.database_rules_reader import RuleAccessDataBase
from error_handlers.imp.delete_strategy.delete_strategy import DeleteErrorHandler
from data_access.imp.gdb_reader.gdb_reader import GdbReader
from enum import Enum
from typing import Dict

class RulesReaderEnum(Enum):
    database_rule_reader = RuleAccessDataBase

class ErrorHandlerEnum(Enum):
    delete_strategy = DeleteErrorHandler

class ReaderDataEnum(Enum):
    gdb_reader =  GdbReader

class ValidationEngine:
    def __init__(self,thematic:str,  reader: str, rules_reader: str, error_handler: str, **kwargs):

        self.reader: IDataReader = ReaderDataEnum[reader].value(**kwargs)
        self.thematic: str = thematic
        self.rules: IRulesReader = RulesReaderEnum[rules_reader].value(thematic)
        self.error_handler: IErrorHandler  = ErrorHandlerEnum[error_handler].value()
        self.data: Dict = None
        self.kwargs = kwargs
        self.reader.validate_inputs()

    def run(self):
        self.data = self.rules.get_data(self.reader)
        for table_name in self.data.keys():
            self.kwargs['table_name'] = table_name
            for validator in self.rules.get_validators(table_name):
                kwargs_validator = self.rules.get_validate_args(validator, **self.kwargs)
                valitor_inst = validator(**kwargs_validator)
                valitor_inst.validate_inputs()
                self.data = valitor_inst.validate(self.data)


            self.data = self.error_handler.handle(self.data, **self.kwargs)
        return self.data