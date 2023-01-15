# Offline loader utility adapted from
# https://github.com/TomSchimansky/TkinterMapView/blob/main/examples/load_offline_tiles.py
# This scripts creates a database with offline tiles. 

import tkintermapview
import pathlib
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

# specify the region to load
north_west_map_corner = (50.2370806, 8.3191687)
south_east_map_corner = (49.8087210, 9.0154272)
zoom_min = 0
zoom_max = 16

# specify path and name of the database
database_path = pathlib.Path(config["FILEPATH"]["MapDatabase"]).absolute().as_posix()

# create OfflineLoader instance
loader = tkintermapview.OfflineLoader(path=database_path)

# save the tiles to the database, an existing database will extended
loader.save_offline_tiles(north_west_map_corner, south_east_map_corner, zoom_min, zoom_max)

# You can call save_offline_tiles() multiple times and load multiple regions into the database.
# You can also pass a tile_server argument to the OfflineLoader and specify the server to use.
# This server needs to be then also set for the TkinterMapView when the database is used.
# You can load tiles of multiple servers in the database. Which one then will be used depends on
# which server is specified for the TkinterMapView.

# print all regions that were loaded in the database
loader.print_loaded_sections()
