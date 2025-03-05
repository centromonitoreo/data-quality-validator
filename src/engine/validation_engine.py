
from data_access.interface import IDataReader
from error_handlers.interface import IErrorHandler
from rule_access.interface import IRulesReader
from rule_access.imp.database_reader.database_rules_reader import RuleAccessDataBase
from error_handlers.imp.delete_strategy.delete_strategy import DeleteErrorHandler
from enum import Enum

class RulesReaderEnum(Enum):
    database_rule_reader: RuleAccessDataBase

class ErrorHandlerEnum(Enum):
    delete_strategy: DeleteErrorHandler

class ValidationEngine:
    def __init__(self,thematic:str,  reader: str, rules_reader: str, error_handler: str, **kwargs):

        self.reader: IDataReader = reader
        self.thematic: str = thematic
        self.rules: IRulesReader = RuleAccessDataBase[rules_reader]
        self.error_handler: IErrorHandler  = ErrorHandlerEnum[error_handler]
        self.data = None
        self.kwargs = kwargs

    def run(self):
        self.data = self.reader.read_data(self.thematic, **self.kwargs)
        for validator in self.rules.get_validators(self.thematic, **self.kwargs):
            kwargs_validator = self.rules.get_validate_args(validator)
            self.data = validator.validate(self.data, **kwargs_validator)
            self.data = self.error_handler.handle(self.data, **self.kwargs)
        return self.data