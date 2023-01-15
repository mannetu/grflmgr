import logging

import fitparse

from .parser import Parser, parser


class FitParser(Parser):
    def parse(self, fname) -> None:
        with open(fname, "rb") as fobj:
            try:
                self._raw_content = fitparse.FitFile(fobj)
            except (fitparse.utils.FitEOFError,
                    fitparse.utils.FitHeaderError) as err:
                raise

            # get device data
            try:
                device = self._raw_content.get_messages("device_info")
                self.device_data = list(device)[0].get_values()
            except (KeyError, IndexError):
                logging.error(
                    f"Could not collect device info. Caught exception {err}")
                raise

            # get session data
            try:
                session = self._raw_content.get_messages("session")
                self.session_data = list(session)[0].get_values()
            except (KeyError, IndexError):
                logging.error(
                    f"Could not collect session info. Caught exception {err}")
                raise

            # get track data
            try:
                datapoints = self._raw_content.get_messages("record")
                datapoints = [_process_fit_record(r) for r in datapoints]
                tr_data = [r for r in datapoints if "lat" in r]
                self.track_data = list()
                self.track_data = tr_data
            except (KeyError, IndexError) as err:
                logging.error(
                    f"Could not collect track info. Caught exception {err}")
                raise


# helper functions
def _process_fit_record(record: dict) -> dict:
    """Extract data from record from fit file."""
    processed_record = {}
    for record_data in record:
        value = record_data.value
        name = record_data.name
        if name == "position_lat":
            processed_record["lat"] = _to_degree(value)
        if name == "position_long":
            processed_record["lon"] = _to_degree(value)
        processed_record[record_data.name] = record_data.value
    return processed_record


def _to_degree(semicircles: int) -> float:
    """Convert semicircles to degrees"""
    return semicircles * (180 / (2**31))


parser.register_parser(".fit", FitParser)
