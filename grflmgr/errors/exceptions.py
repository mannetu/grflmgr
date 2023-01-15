import configparser
import logging

config = configparser.ConfigParser()
config.read("config.ini")


class GrflmgrError(Exception):
    pass


class GrflmgrWarning(Exception):
    pass


class GrflmgrNoTrack(Exception):
    pass
