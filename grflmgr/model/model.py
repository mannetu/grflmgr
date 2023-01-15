from .fileimporter import FileImporter
from .database import DatabaseHandler


class Model:
    def __init__(self):
        self.database = DatabaseHandler()

    def fileimporter(self):
        return FileImporter(self)
