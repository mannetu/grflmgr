import configparser
import logging
import pathlib
import hashlib
from collections import deque
import threading
from sqlalchemy import inspect, select
from datetime import datetime
import pprint as pp

import fitparse

from errors import GrflmgrNoTrack
from .parser import parser
from .record import Record, Trackpoint


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
                logging.warning(
                    f"'{self._file.name}' not found. Caught exception: {err}")
            except GrflmgrNoTrack:
                n_error += 1
                logging.warning(
                    f"'{fname.name}': Does not contain track.")
            except Exception as err:
                n_error += 1
                logging.error(
                    f"'{fname.name}': Unknown import error. Caught exception: {err}")
                raise
            finally:
                callback((n_imported, n_duplicate, n_error, n_total))

    def import_file(self, fname: pathlib.Path) -> int:
        if not fname.is_file():
            raise IsADirectoryError

        with open(fname, "rb") as fobj:

            # check if file was already imported:
            as_bytes = fobj.read()
            hash = hashlib.md5(as_bytes).hexdigest()

            if self.is_file_imported(hash):
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
            p_data = p.get_data()
            logging.info(f"'{fname.name}': Parsing successful")
            if len(p_data.ptrack) == 0:
                raise GrflmgrNoTrack
            self.add_activity(fname=fname.name, fhash=hash, p_data=p_data)
            return self.SUCCESS

    def add_activity(self, fname, fhash, p_data):
        if config['ENV']['Env'] == 'Development':
            pp.pprint(p_data.get_dict(1))

        trpoints = []
        for trpoint in p_data.ptrack:
            mapper = inspect(Trackpoint)
            trp = Trackpoint()
            order = 0
            for col in  mapper.attrs:
                trp.__setattr__(col.key, trpoint.get(col.key, None))
                trp.__setattr__('order', order)
                order += 1
            trpoints.append(trp)

        if len(trpoints) > 0:
            nwc_lat, nwc_lon, sec_lat, sec_lon = get_map_corners(trpoints)

        rec = Record(
            filename=fname,
            filehash=fhash,
            import_timestamp=datetime.now(),

            # track data
            trackpoints=trpoints,
            nwc_lat=nwc_lat,
            nwc_lon=nwc_lon,
            sec_lat=sec_lat,
            sec_lon=sec_lon,

            # device data
            descriptor=p_data.device.get('descriptor', None),
            manufacturer=p_data.device.get('manufacturer', None),
            product_name=p_data.device.get('product_name', None),
            garmin_product=p_data.device.get('garmin_product', None),
            device_timestamp=p_data.device.get('timestamp', None),

            # session data
            sport=p_data.act_session.get('sport', None),
            start_time=p_data.act_session.get('start_time', None),
            session_timestamp=p_data.act_session.get('timestamp', None),
            avg_speed=p_data.act_session.get('avg_speed', None),
            max_speed=p_data.act_session.get('max_speed', None),
            min_altitude=p_data.act_session.get('min_altitude', None),
            avg_altitude=p_data.act_session.get('avg_altitude', None),
            max_altitude=p_data.act_session.get('max_altitude', None),
            max_neg_grade=p_data.act_session.get('max_neg_grade', None),
            avg_grade=p_data.act_session.get('avg_grade', None),
            max_pos_grade=p_data.act_session.get('max_pos_grade', None),
            avg_temperature=p_data.act_session.get('avg_temperature', None),
            max_temperature=p_data.act_session.get('max_temperature', None),
            min_heart_rate=p_data.act_session.get('min_heart_rate', None),
            avg_heart_rate=p_data.act_session.get('avg_heart_rate', None),
            max_heart_rate=p_data.act_session.get('max_heart_rate', None),
            total_ascent=p_data.act_session.get('total_ascent', None),
            total_descent=p_data.act_session.get('total_descent', None),
            total_distance=p_data.act_session.get('total_distance', None),
            total_timer_time=p_data.act_session.get('total_timer_time', None),
            total_elapsed_time=p_data.act_session.get('total_elapsed_time', None),
            total_calories=p_data.act_session.get('total_calories', None)
        )

        # add activity to database
        with self.model.db_session() as s:
            s.add(rec)
            s.commit()

    def is_file_imported(self, hash):
        stmt = select(Record.filehash).where(Record.filehash == hash)
        with self.model.db_session() as s:
            result = s.execute(stmt).scalar()
        return result


# helper function
def get_map_corners(trpoints) -> tuple:
    """Determines the max/min lats and longs of the north-west and 
    south-east map corner to cover respective track.
    """
    track = [(p.lat, p.lon) for p in trpoints]
    lats = []
    longs = []
    for position in track:
        lats.append(position[0])
        longs.append(position[1])
    nwc_lat = max(lats)
    nwc_lon = min(longs)
    sec_lat = min(lats)
    sec_lon = max(longs)
    return (nwc_lat, nwc_lon, sec_lat, sec_lon)
