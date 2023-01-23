import configparser
import pathlib
import tkinter as tk
from tkinter import ttk
from tkintermapview import TkinterMapView

config = configparser.ConfigParser()
config.read("config.ini")


class View(ttk.Frame):

    PAD = 5
    RELIEF = "groove"
    BORDERWIDTH = 2

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=tk.TRUE)
        self.columnconfigure(0, weight=2)  # Button and list frames
        self.columnconfigure(1, weight=2)  # Map frame
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self._make_btn_frame()
        self._make_list_frame()
        self._make_map_frame()

        self.controller = None
        self.shown_rides = []

    def set_controller(self, controller):
        self.controller = controller

    # Button Frame
    def _make_btn_frame(self):
        """
        Frame with control buttons
        """
        self.btn_box = ttk.Frame(
            self, relief=self.RELIEF, borderwidth=self.BORDERWIDTH)
        self.btn_box.grid(column=0, row=0, padx=self.PAD,
                          pady=self.PAD, sticky=tk.NSEW)

        self.import_btn = ttk.Button(
            self.btn_box, text="Import Folder", command=self.import_btn_clicked
        )
        self.import_btn.grid(column=0, row=0, padx=self.PAD, pady=self.PAD)

        self.update_btn = ttk.Button(
            self.btn_box, text="Update", command=self.update_btn_clicked
        )
        self.update_btn.grid(column=1, row=0, padx=self.PAD, pady=self.PAD)

        self.message_label = ttk.Label(self.btn_box, text="", foreground="red")
        self.message_label.grid(
            column=0, columnspan=3, row=1, padx=self.PAD, pady=self.PAD, sticky=tk.NW
        )

    def import_btn_clicked(self):
        if self.controller:
            self.controller.import_folder()

    def update_btn_clicked(self):
        if self.controller:
            self.controller.update_ride_list()

    def set_filter_new(self):
        if self.controller:
            self.controller.set_filter_new(self.filter_new_checkbox_var.get())

    def set_filter_fav(self):
        if self.controller:
            self.controller.set_filter_fav(self.filter_fav_checkbox_var.get())

    def set_autozoom(self):
        if self.controller:
            self.controller.show_tracks(self.shown_rides)

    def show_error(self, message):
        self.message_label["text"] = message
        self.message_label["foreground"] = "red"
        #self.message_label.after(5000, self.hide_message)

    def show_success(self, message):
        self.message_label["text"] = message
        self.message_label["foreground"] = "green"
        #self.message_label.after(20000, self.hide_message)

    def hide_message(self):
        self.message_label["text"] = ""

    # List Frame
    def _make_list_frame(self):
        self.filter_new_checkbox_var = tk.BooleanVar()
        self.filter_fav_checkbox_var = tk.BooleanVar()
        self.autozoom_checkbox_var = tk.BooleanVar()

        self.list_frame = ttk.Frame(
            self, relief=self.RELIEF, borderwidth=self.BORDERWIDTH
        )
        self.list_frame.columnconfigure(3, weight=1)
        self.list_frame.rowconfigure(0, weight=0)

        self.list_frame.grid(
            column=0,
            row=1,
            padx=self.PAD,
            pady=self.PAD,
            sticky=tk.NSEW,
        )

        self.filter_lbl = ttk.Label(self.list_frame, text="Filter:")
        self.filter_lbl.grid(column=0, row=0, padx=self.PAD,
                             pady=self.PAD, sticky=tk.W)

        self.filter_new_checkbox = ttk.Checkbutton(
            self.list_frame,
            text="New",
            command=self.set_filter_new,
            variable=self.filter_new_checkbox_var,
        )
        self.filter_new_checkbox.grid(column=1, row=0, sticky=tk.W)

        self.filter_fav_checkbox = ttk.Checkbutton(
            self.list_frame,
            text="Favs",
            command=self.set_filter_fav,
            variable=self.filter_fav_checkbox_var,
        )
        self.filter_fav_checkbox.grid(column=2, row=0, sticky=tk.W)

        self.autozoom_checkbox = ttk.Checkbutton(
            self.list_frame,
            text="Autozoom",
            command=self.set_autozoom,
            variable=self.autozoom_checkbox_var,
        )
        self.autozoom_checkbox.grid(column=3, row=0, sticky=tk.E)

        # ride table
        self.ride_list = ttk.Frame(self.list_frame)
        self.ride_list.grid(
            column=0, columnspan=4, row=1, padx=self.PAD, pady=self.PAD, sticky=tk.NSEW
        )
        self.ride_list.columnconfigure(0, weight=1)

        columns = ("ride_id", "ride_date", "ride_distance")
        self.tree = ttk.Treeview(
            self.ride_list, columns=columns, height=30, show="headings"
        )

        self.tree.grid(column=0, row=1, sticky=tk.NSEW)

        # define headings
        self.tree.column("ride_id", anchor=tk.W, width=200, stretch=tk.YES)
        self.tree.heading("ride_id", text="ID", anchor=tk.W)
        self.tree.column("ride_date", anchor=tk.CENTER, width=60, stretch=tk.YES)
        self.tree.heading("ride_date", text="Date", anchor=tk.CENTER)
        self.tree.column("ride_distance", anchor=tk.CENTER,
                         width=60, stretch=tk.YES)
        self.tree.heading("ride_distance", text="Dist [km]", anchor=tk.CENTER)

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.ride_list, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=3, sticky=tk.NS)

        # selection handler
        def item_selected(event):
            self.shown_rides = []
            for selected_ride in self.tree.selection():
                ride_id = self.tree.item(selected_ride)["values"][0]
                self.shown_rides.append(ride_id)
            self.controller.show_tracks(self.shown_rides)

        self.tree.bind("<<TreeviewSelect>>", item_selected)

    def clear_ridelist(self):
        # clear the treeview list items
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert_ridelist(self, ride: str):
        self.tree.insert(
            "",
            tk.END,
            iid=ride.id,
            values=(
                ride.id,
                ride.start_time.strftime("%d.%m.%y"),
                round((ride.total_distance / 1000),1),
            ),
        )

    # Map Frame
    def _make_map_frame(self):
        self.map_frame = ttk.Frame(
            self, relief=self.RELIEF, borderwidth=self.BORDERWIDTH
        )
        self.map_frame.grid(
            column=1, row=0, rowspan=2, padx=self.PAD, pady=self.PAD, sticky=tk.NSEW,
        )

        self._make_map()

    def _make_map(self):
        path = config['FILEPATH']['Database']
        pathlib.Path(pathlib.Path.home(), path).mkdir(parents=True, exist_ok=True)
        tilesdb_path = pathlib.Path(pathlib.Path.home(), path, 'offline_tiles.db')
        
        self.map_widget = TkinterMapView(
            self.map_frame,
            width=int(config["MAP"]["MapWidth"]),
            height=int(config["MAP"]["MapHeight"]),
            corner_radius=0,
            database_path=tilesdb_path.absolute().as_posix()
        )
        self.map_widget.pack(fill=tk.BOTH, expand=tk.TRUE)

        self.map_widget.set_address(config["MAP"]["MapPosition"])
        self.map_widget.set_zoom(int(config["MAP"]["MapZoom"]))

    def set_map_zoom(self, corner_nw, corner_se):
        if self.autozoom_checkbox_var.get():
            self.map_widget.fit_bounding_box(corner_nw, corner_se)

    def show_tracks(self, tracks):
        self.map_widget.delete_all_path()
        for track in tracks:
            self.map_widget.set_path(track, width=config["MAP"]["TrackWidth"])