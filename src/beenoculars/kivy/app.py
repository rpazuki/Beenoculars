import logging
import os

import kivy
from kivy.lang import Builder  # type: ignore
from kivy.logger import Logger  # type: ignore

import beenoculars.core as core
from beenoculars.core import ProcessesRegistry
from beenoculars.kivy import KivyMultiLayoutApp  # , Layout
from beenoculars.kivy.image_processing import ToKivyImage, ToOpenCVImage
from beenoculars.kivy.layouts import LogViewLayout, TopToolbarLayout

logging.root = Logger

kivy.require('1.8.0')  # type: ignore
log = logging.getLogger(__name__)


class KivyApp(KivyMultiLayoutApp):
    def __init__(self, **kwargs):
        #
        self.main_layout = TopToolbarLayout(self)
        super(KivyApp, self).__init__(
            init_layout=self.main_layout,
            **kwargs)
        self.layout = self.main_layout

    def show_main(self):
        self.show_layout(self.main_layout)

    def show_log(self):
        self.show_layout(LogViewLayout(self))


def create_app():
    log.info("Beenoculars app stars")
    registry = ProcessesRegistry()
    registry[core.ToOpenCVImage] = ToOpenCVImage()
    registry[core.ToFrameworkImage] = ToKivyImage()
    app = KivyApp()
    return app


if __name__ == '__main__':
    log.info("Debug main is called.")
    Builder.load_file(os.path.abspath(
        "beenoculars/src/beenoculars/kivy/layouts.kv"))
    log.info("KV is loaded.")
    create_app().run()
