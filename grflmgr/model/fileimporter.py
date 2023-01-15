import configparser
import logging
import pathlib
import hashlib
import threading
from collections import deque

import fitparse

from errors import GrflmgrNoTrack
from .parser import parser

config = configparser.ConfigParser()
config.read("config.ini")


class FileImporter():

    SUCCESS = True
    DUPLICATE = False

    def __init__(self, model):
        self.model = model

        self.n_imported = 0

    def import_folder(self, foldername: pathlib.Path, callback) -> tuple[int, int]:
        if not foldername.is_dir():
            raise NotADirectoryError

        fnames = deque()
        for ftype in parser.get_supported_ftypes():
            for f in foldername.glob('*' + ftype):
                fnames.append(f)

        thread = threading.Thread(
            target=self.import_folder_task, args=(fnames, callback))
        thread.start()
        self.n_imported = 0

    def import_folder_task(self, fnames, callback):
        n_imported = 0
        n_duplicate = 0
        n_error = 0
        n_total = len(fnames)

        while len(fnames) > 0:
            fname = fnames.popleft()
            try:
                result = self.import_file(fname)
                if result == self.SUCCESS:
                    n_imported += 1
                elif result == self.DUPLICATE:
                    n_duplicate += 1
                else:
                    n_error += 1
            except FileNotFoundError as err:
                n_error += 1
                logging.warning(f"'{self._file.name}' not found. Caught exception: {err}")
            except GrflmgrNoTrack:
                n_error += 1
                logging.warning(
                    f"'{fname.name}': Does not contain track.")
            except Exception as err:
                n_error += 1
                logging.error(
                    f"'{fname.name}': Unknown import error. Caught exception: {err}")
            finally:
                callback((n_imported, n_duplicate, n_error, n_total))

    def import_file(self, fname: pathlib.Path) -> int:
        if not fname.is_file():
            raise IsADirectoryError

        with open(fname, "rb") as fobj:

            # check if file was already imported:
            as_bytes = fobj.read()
            hash = hashlib.md5(as_bytes).hexdigest()

            if self.model.database.is_file_imported(hash):
                logging.info(
                    f"'{fname.name}' has already been imported ({hash})")
                return self.DUPLICATE

        # parse activity file
        try:
            p = parser.get_parser(fname.suffix)
            p.parse(fname)
        except NotImplementedError:
            logging.info(
                f"'{fname.name}': '{fname.suffix}' not supported")
        except (fitparse.utils.FitEOFError, fitparse.utils.FitHeaderError) as err:
            logging.warning(
                f"'{fname.name}': {p.__class__.__name__} failed. Caught exception: {err}")
        except Exception as err:
            logging.error(
                f"'{fname.name}': {p.__class__.__name__} - unknown error. Caught exception: {err}")
        else:
            activity = p.get_activity()
            logging.info(f"'{fname.name}': Parsing successful")
            activity._filehash = hash
            if len(activity._track) > 0:
                activity.get_map_corners()
            else:
                raise GrflmgrNoTrack

            self.model.database.add_activity(activity)
            return self.SUCCESS
