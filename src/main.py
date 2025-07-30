import os

from dotenv import load_dotenv
import geopandas as gpd

from engine.validation_engine import ValidationEngine
from rule_access.imp.database_reader.config import Base, SessionManager
from rule_access.imp.database_reader.models.thematic import Thematic


def validate_data(
    thematic: str, rule_reader: str, erro_handlers: str, data_reader: str, **kwargs
):
    validation_engine = ValidationEngine(
        thematic, data_reader, rule_reader, erro_handlers, **kwargs
    )
    return validation_engine.run()


def save_data(dict_data, out_folder):
    for keys, data in dict_data.items():
        if isinstance(data, gpd.GeoDataFrame):
            data.to_file(os.path.join(out_folder, f"{keys}.shp"))
        else:
            data.to_csv(os.path.join(out_folder, f"{keys}.csv"))



if __name__ == "__main__":
    
    load_dotenv()
    pg_conn_string = os.getenv("PG_DATABASE_URL")
    out_folder = r"D:\1.PROCESOS_CDM\11.CALIDAD_BDC\02.HERRAMIENTAS\Procesos\cienaga\salida"
    thematics = SessionManager().get_session().query(Thematic).all()
    for thematic in thematics:
        print(thematic.group_name)
        data = validate_data(
            thematic.group_name,
            "database_rule_reader",
            "delete_strategy",
            "postgres_reader",
            pg_conn_string=pg_conn_string,
        )
        save_data(data, out_folder)
