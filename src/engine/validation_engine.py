
from data_access.interface import IDataReader
from error_handlers.interface import IErrorHandler
from rule_access.interface import IRulesReader


class ValidationEngine:
    def __init__(self, reader: IDataReader, rules: IRulesReader, error_handler: IErrorHandler):

        self.reader = reader
        self.rules = rules
        self.error_handler = error_handler
        self.data = None

    def run(self):
        data = self.reader.read_data()
        for validator in self.rules.get_validators():
            self.data = validator.validate(self.data)
            self.data = self.error_handler.handle(self.data)
        return self.data