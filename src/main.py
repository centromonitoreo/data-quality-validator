import os
import pickle

from dotenv import load_dotenv

from engine.validation_engine import ValidationEngine
from data_access.imp.postgres_reader.postgres_reader import EXPEDIENTES
from rule_access.imp.database_reader.config import SessionManager
from rule_access.imp.database_reader.models.thematic import Thematic


def validate_data(
    thematic: str, rule_reader: str, erro_handlers: str, data_reader: str, **kwargs
):
    validation_engine = ValidationEngine(
        thematic, data_reader, rule_reader, erro_handlers, **kwargs
    )
    return validation_engine.run()


def save_data(dict_data, out_folder, expediente_name):
    os.makedirs(out_folder, exist_ok=True)
    with open(os.path.join(out_folder, f"{expediente_name}.pkl"), "wb") as f:
        pickle.dump(dict_data, f)

if __name__ == "__main__":

    load_dotenv()
    pg_conn_string = os.getenv("PG_DATABASE_URL")
    out_folder = r"D:\Codigos CM\programa_compilacion\areas_compiladas\luisa"
    session = SessionManager().get_session()
    thematics = session.query(Thematic).all()

    for expediente in EXPEDIENTES:
        print(f"Procesando expediente: {expediente}")
        expediente_data = {}
        for thematic in thematics:
            print(thematic.group_name)
            data = validate_data(
                thematic.group_name,
                "database_rule_reader",
                "delete_strategy",
                "postgres_reader",
                pg_conn_string=pg_conn_string,
                expediente=expediente,
            )
            expediente_data[thematic.group_name] = data

        save_data(expediente_data, out_folder, expediente)
