import logging
import configparser
import pathlib

config = configparser.ConfigParser()
config.read("config.ini")


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def import_folder(self, foldername: pathlib.Path = None):
        if foldername == None:
            foldername = pathlib.Path(pathlib.Path.home(), config["FILEPATH"]["ImportFolder"])
        try:
            self.model.fileimporter().import_folder(
                foldername, self.import_folder_cb)
        except Exception as err:
            self.view.show_error(f"Folder import failed")
            logging.warning(
                f"Folder import from {foldername} failed with unknown error: {err}")
            raise

    def import_folder_cb(self, import_stats: tuple):
        n_imp, n_dupl, n_err, n_tot = import_stats
        percent_imported = round(100*((n_imp + n_dupl + n_err) / n_tot))

        # self.update_ride_list()
        if percent_imported < 100:
            self.view.show_success(f"Imported... {percent_imported}%.")
        else:
            self.view.show_success(
                f"{n_imp} files imported. Rejected {n_dupl} duplicates and {n_err} files with error.")

    def update_ride_list(self):
        self.view.clear_ridelist()
        for activity in self.model.query.get_ridelist():
            self.view.insert_ridelist(activity)
        logging.debug(
            f"Updated ride list: {self.view.tree.get_children()}\n"
        )

    def set_filter_new(self, state: bool):
        logging.debug(f"Filter New: {state}")

    def set_filter_fav(self, state: bool):
        logging.debug(f"Filter Fav: {state}")

    def show_tracks(self, ride_ids):
        if len(ride_ids) == 0:
            return

        tracks = []
        lats = []
        lons = []
        for ride_id in ride_ids:
            tracks.append(self.model.query.get_track(ride_id))
            nwc_lat, nwc_lon, sec_lat, sec_lon = self.model.query.get_map_borders(ride_id)
            lats.append(nwc_lat)
            lats.append(sec_lat)
            lons.append(nwc_lon)
            lons.append(sec_lon)
        nw_corner = (max(lats), min(lons))
        se_corner = (min(lats), max(lons))

        self.view.set_map_zoom(nw_corner, se_corner)
        self.view.show_tracks(tracks)
        logging.debug(f"Showing tracks {ride_ids}")
