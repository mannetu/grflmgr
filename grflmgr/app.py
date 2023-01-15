import tkinter as tk
from tkinter import ttk
import configparser
import logging
import os

from model import Model
from controller import Controller
from view import View


VERSION = '0.1'

config = configparser.ConfigParser()
config.read("config.ini")

logging.basicConfig(format="%(asctime)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s",
                    level=config["LOGGING"]["Level"])

if os.name == "nt":
    logging.info("Running on Windows")
    # resolve issue with high dpi display on windows 10
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(f"Greffel Manager {VERSION}")
        self.geometry(
            f"{config['WINDOW']['MainWidth']}x{config['WINDOW']['MainHeight']}"
        )

        # create a model
        model = Model()

        # create a view and place it on the root window
        view = View(self)

        # create a controller
        controller = Controller(model, view)

        # set the controller to view
        view.set_controller(controller)


if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()

    except Exception as err:
        logging.warning(f"Unexpected error: {err=}")
        raise

    finally:
        logging.info("Exiting Greffel Manager. Ride on!\n")
