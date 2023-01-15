import configparser
import pprint as pp

config = configparser.ConfigParser()
config.read("config.ini")


class DatabaseHandler:
    def __init__(self):
        self.db = []

    def add_activity(self, activity):
        if config['ENV']['Env'] == 'Development':
            pp.pprint(activity.get_dict(1))
        self.db.append(activity)

    def is_file_imported(self, hash):
        if any(activity._filehash == hash for activity in self.db):
            return True

    def get_track(self, hash):
        x = list(filter(lambda activity: activity._filehash == hash, self.db))
        track = x[0].get_track()
        return track

    def get_map_zoom(self, hash):
        x = list(filter(lambda activity: activity._filehash == hash, self.db))
        corners = (x[0]._session["corner_nw"], x[0]._session["corner_se"])
        return corners
