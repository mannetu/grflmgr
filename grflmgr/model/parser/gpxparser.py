import gpxpy

from .parser import Parser, parser


class GpxParser(Parser):
    def parse(self, fname):
        with open(fname, "r") as fobj:
            try:
                self._raw_content = gpxpy.parse(fobj)
            except Exception as err:
                raise

        # get device data

        # get track data
        track = []
        for gpxtrack in self._raw_content.tracks:
            for segment in gpxtrack.segments:
                for point in segment.points:
                    point_dict = {'lat': point.latitude, 'lon': point.longitude,
                                  'enhanced_altitude': point.elevation, 'timestamp': point.time}
                    track.append(point_dict)
        self.track_data = track

        # for waypoint in gpx.waypoints:
        #     print('waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude))

        # for route in gpx.routes:
        #     print('Route:')
        #     for point in route.points:
        #         print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))

        # get session data
        self.session_data['timestamp'] = self._raw_content.get_time_bounds()[0]
        self.session_data["total_distance"] = self._raw_content.get_moving_data()[2]

parser.register_parser(".gpx", GpxParser)
