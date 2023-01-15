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
            foldername = pathlib.Path(config["FILEPATH"]["ImportPath"])
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
        for activity in self.model.database.db:
            self.view.insert_ridelist(activity)
        logging.debug(
            f"Updated ride list: {self.view.tree.get_children()}\n"
        )

    def set_filter_new(self, state: bool):
        logging.debug(f"Filter New: {state}")

    def set_filter_fav(self, state: bool):
        logging.debug(f"Filter Fav: {state}")

    def show_tracks(self, rides):
        if len(rides) == 0:
            return
        tracks = []
        max_positions = []
        for ride in rides:
            tracks.append(self.model.database.get_track(ride))

            nw, se = self.model.database.get_map_zoom(ride)
            max_positions.append(nw)
            max_positions.append(se)

        lats = []
        longs = []
        for position in max_positions:
            lats.append(position[0])
            longs.append(position[1])
        corner_nw = (max(lats), min(longs))
        corner_se = (min(lats), max(longs))

        self.view.set_map_zoom(corner_nw, corner_se)
        self.view.show_tracks(tracks)
        logging.debug(f"Showing tracks {rides}")
