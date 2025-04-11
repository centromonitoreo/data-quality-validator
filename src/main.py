from engine.validation_engine import ValidationEngine
from rule_access.imp.database_reader.config import Base


def validate_data(
    thematic: str, rule_reader: str, erro_handlers: str, data_reader: str, **kwargs
):
    validation_engine = ValidationEngine(
        thematic, data_reader, rule_reader, erro_handlers, **kwargs
    )
    return validation_engine.run()


if __name__ == "__main__":
    path_gdb = r"D:\1.PROCESOS_CDM\11.CALIDAD_BDC\02.HERRAMIENTAS\Procesos\cienaga\BD_ANLA_MAGNA_NACIONAL.gdb" # r"C:\Users\Jhon\Downloads\BD_ANLA_MAGNA_NACIONAL.gdb" # r"F:\ANLA\2025\04_Proceso_validacion\Pruebas\LAM0150\20246201130532\ICA_LAM0150_2023.gdb"
    data = validate_data(
        "MuestreoSuelo", # "Monitoreo Atmosferico" "Monitoreo Agua Superficial"
        "database_rule_reader",
        "delete_strategy",
        "gdb_reader",
        path_gdb=path_gdb,
    )
    print('holi')
