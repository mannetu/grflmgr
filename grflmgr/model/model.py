import configparser
import pathlib
from sqlalchemy import create_engine

from .record import init_db
from .fileimporter import FileImporter
from .query import RecordQuery


config = configparser.ConfigParser()
config.read("config.ini")


class Model:
    def __init__(self):
        path = config['FILEPATH']['Database']
        pathlib.Path(pathlib.Path.home(), path).mkdir(
            parents=True, exist_ok=True)
        db_path = pathlib.Path(pathlib.Path.home(), path,
                               'records.db').absolute().as_posix()

        engine = create_engine("sqlite+pysqlite:///" +
                               db_path, echo=False, future=True)
        self.db_session = init_db(engine)

        self.query = RecordQuery(self.db_session)

    def fileimporter(self):
        return FileImporter(self)
