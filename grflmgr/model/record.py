import configparser
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


config = configparser.ConfigParser()
config.read("config.ini")


Base = declarative_base()


class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True)

    # record data
    filename = Column(String)
    filehash = Column(String)
    import_timestamp = Column(DateTime)

    # track data
    trackpoints = relationship("Trackpoint")

    # device data
    descriptor = Column(String)  # 'ELEMNT BOLT 8072'
    manufacturer = Column(String)  # 'wahoo_fitness'
    product_name = Column(String)  # 'ELEMNT BOLT'
    garmin_product = Column(String)  # 'edge500'
    device_timestamp = Column(DateTime)  # datetime.datetime()

    # session data
    sport = Column(String)  # 'cycling'
    start_time = Column(DateTime)  # datetime.datetime()
    session_timestamp = Column(DateTime)  # datetime.datetime()
    nwc_lat = Column(Float)  # 50.723746279254556
    nwc_lon = Column(Float)  # 8.990853549912572
    sec_lat = Column(Float)  # 50.01621348783374
    sec_lon = Column(Float)  # 9.739641565829515
    avg_speed = Column(Float)  # 3.809
    max_speed = Column(Float)  # 13.62
    min_altitude = Column(Float)  # 121.39999999999998
    avg_altitude = Column(Float)  # 288.6
    max_altitude = Column(Float)  # 437.20000000000005
    max_neg_grade = Column(Float)  # -12.36
    avg_grade = Column(Float)  # 0.95
    max_pos_grade = Column(Float)  # 14.37
    avg_temperature = Column(Integer)  # 10
    max_temperature = Column(Integer)  # 30
    min_heart_rate = Column(Integer)  # 86
    avg_heart_rate = Column(Integer)  # 119
    max_heart_rate = Column(Integer)  # 141
    total_ascent = Column(Integer)  # 2422
    total_descent = Column(Integer)  # 2240
    total_distance = Column(Float)  # 136572.73
    total_timer_time = Column(Float)  # 35859.0
    total_elapsed_time = Column(Float)  # 54105.0
    total_calories = Column(Integer)  # 6619

    def __repr__(self):
        return f"Record {self.id!r}: (filename={self.filename!r}, hash={self.filehash!r}, timestamp={str(self.timestamp)!r})"


class Trackpoint(Base):
    __tablename__ = "trackpoints"
    id = Column(Integer, primary_key=True)
    order = Column(Integer)

    position_lat = Column(Integer)  # 596718251
    position_long = Column(Integer)  # 107303276
    lat = Column(Float)  # 50.01634600572288
    lon = Column(Float)  # 8.994056694209576
    altitude = Column(Float)  # 128.60000000000002
    distance = Column(Float)  # 0.0
    speed = Column(Float)  # 0.0
    heart_rate = Column(Integer)  # 109
    temperature = Column(Integer)  # 8
    timestamp = Column(DateTime)  # datetime.datetime(2022, 4, 6, 5, 11, 32)

    record_id = Column(Integer, ForeignKey("records.id"))

    def __repr__(self):
        return (f"Trackpoint {self.id!r}: position=({self.position_lat!r},{self.position_long!r})), altitute={self.altitude!r}")


def init_db(engine):
    Base.metadata.create_all(engine, checkfirst=True)
    Session = sessionmaker(bind=engine)
    return Session
