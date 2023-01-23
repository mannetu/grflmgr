from collections import namedtuple


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

    def get_data(self):
        ParserData = namedtuple(
            'ParserData', ['device', 'act_session', 'ptrack'])
        parser_data = ParserData(
            self.device_data, self.session_data, self.track_data)
        return parser_data


