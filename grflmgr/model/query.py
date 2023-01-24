from sqlalchemy import select

from .record import Record, Trackpoint


class RecordQuery:
    def __init__(self, db_session) -> None:
        self.db_session = db_session

    def get_ridelist(self):
        stmt = select(Record.id, Record.start_time, Record.total_distance, Record.total_timer_time).order_by(
            Record.start_time.desc())
        with self.db_session() as s:
            result = s.execute(stmt).all()
        return result

    def get_track(self, ride_id):
        stmt = select(Trackpoint.lat, Trackpoint.lon).where(
            Trackpoint.record_id == ride_id).order_by(Trackpoint.order)
        with self.db_session() as s:
            result = s.execute(stmt).all()
        return result

    def get_map_borders(self, ride_id):
        stmt = select(Record.nwc_lat, Record.nwc_lon, Record.sec_lat,
                      Record.sec_lon).where(Record.id == ride_id)
        with self.db_session() as s:
            result = s.execute(stmt).first()
            return result  # (nwc_lat, nwc_lon, sec_lat, sec_lon)
