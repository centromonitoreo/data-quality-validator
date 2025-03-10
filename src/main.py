from engine.validation_engine import ValidationEngine
from rule_access.imp.database_reader.config import Base

def validate_data(thematic:str, rule_reader: str, erro_handlers:str, data_reader:str, **kwargs):
    validation_engine = ValidationEngine(thematic, data_reader, rule_reader, erro_handlers, **kwargs)
    validation_engine.run()


if __name__ == '__main__':
    path_gdb= r"C:\Users\Jhon\Downloads\Prueba\02_Estrategia_02-Correspondencia\02_Carpeta_salida-E2_v1\LAM0150\20246201130532\ICA_LAM0150_2023_1.gdb"
    validate_data("Monitoreo Agua Superficial", "database_rule_reader",  "delete_strategy", "gdb_reader", path_gdb = path_gdb )