from engine.validation_engine import ValidationEngine
from rule_access.imp.database_reader.config import Base

def validate_data(thematic:str, rule_reader: str, erro_handlers:str, data_reader:str, **kwargs):
    validation_engine = ValidationEngine(thematic, data_reader, rule_reader, erro_handlers, **kwargs)
    validation_engine.run()


if __name__ == '__main__':
    path_gdb= r'D:\1.PROCESOS_CDM\11.CALIDAD_BDC\02.HERRAMIENTAS\Procesos\Alto San Jorge\Descarga_archivos\LAM1067\2019177955-1-000\BD_ANLA_3115.gdb'
    validate_data("Monitoreo Agua Superficial", "database_rule_reader",  "delete_strategy", "gdb_reader", path_gdb = path_gdb )