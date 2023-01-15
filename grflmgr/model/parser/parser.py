from ..activity import Activity


class ParserFactory:
    def __init__(self):
        self.parsers = {}

    def register_parser(self, key, parser):
        self.parsers[key] = parser

    def get_parser(self, ftype):
        parser = self.parsers.get(ftype)
        if not parser:
            raise ValueError(ftype)
        return parser()

    def get_supported_ftypes(self):
        return list(self.parsers.keys())


parser = ParserFactory()


class Parser:
    def __init__(self):
        self.device_data: dict = {}
        self.session_data: dict = {}
        self.track_data: list = []

        self._raw_content = None
        self._activity = Activity()

    def get_activity(self) -> Activity:
        self._activity = Activity(
            device=self.device_data, session=self.session_data, track=self.track_data
        )
        return self._activity
