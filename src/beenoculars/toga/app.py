"""
Studying bees diseases by analysing photos
"""
import logging

import beenoculars.core as core
from beenoculars.core import ProcessesRegistry
from beenoculars.toga import TogaMultiLayoutApp
from beenoculars.toga.image_processing import ToOpenCVImage, ToTogaImage
from beenoculars.toga.layouts import LogViewLayout, TopToolbarLayout

log = logging.getLogger(__name__)


class TogaApp(TogaMultiLayoutApp):
    """A toga App class that has a layout.

    The layout class will create UI elements and its main_box will be added
    as the app main window's content.
    """

    def __init__(self,
                 formal_name: str,
                 app_id="com.beenoculars"):

        self.main_layout = TopToolbarLayout(self)
        super(TogaApp, self).__init__(init_layout=self.main_layout,
                                      formal_name=formal_name,
                                      app_id=app_id,
                                      )

    def show_main(self):
        self.show_layout(self.main_layout)

    def show_log(self):
        self.show_layout(LogViewLayout(self))


def create_app():
    log.info("Beenoculars app stars")

    registry = ProcessesRegistry()
    registry[core.ToOpenCVImage] = ToOpenCVImage()
    registry[core.ToFrameworkImage] = ToTogaImage()
    app = TogaApp("Beenoculars")
    return app


if __name__ == "__main__":
    log.info("Debug main is called.")
    try:
        create_app().main_loop()
    except Exception as e:
        print(e)
