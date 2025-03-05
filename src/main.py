from engine.validation_engine import ValidationEngine

def validate_data(thematic:str, rule_reader: str, erro_handlers:str, data_reader:str, **kwargs):
    validation_engine = ValidationEngine(thematic, data_reader, rule_reader, erro_handlers, **kwargs)