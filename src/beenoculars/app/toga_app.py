"""
Studying bees diseases by analysing photos
"""
import logging

import beenoculars.image_processing as imp
from beenoculars.app.toga_bindings import init_event_bindings
from beenoculars.core.__core__ import ServiceRegistry, UIFramework
from beenoculars.image_processing import ProcessesRegistry
from beenoculars.toga import LayoutApp
from beenoculars.toga.image_processing import ToCVImageProcess, ToTogaImageProcess
from beenoculars.toga.layouts import TopToolbarLayout

# logger
log = logging.getLogger(__name__)


class BeenocularsTogaTopToolbar(LayoutApp):
    def __init__(self, formal_name: str):
        super().__init__(formal_name=formal_name,
                         app_id="com.beenoculars",
                         layout=TopToolbarLayout()
                         )


def create_app():
    log.info("Beenoculars app stars")

    registry = ProcessesRegistry()
    registry[imp.ToOpenCVImageProcess] = ToCVImageProcess()
    registry[imp.ToFrameworkImageProcess] = ToTogaImageProcess()
    ServiceRegistry().ui_framework = UIFramework.TOGA
    #
    # toOpenCV = registry[imp.ToOpenCVImageProcess]
    # toFramework = registry[imp.ToFrameworkImageProcess]
    # p1 = imp.OverlayContours @ {'selected_qs': (20, 80)}
    # p2 = imp.OverlayContours @ {'selected_qs': (1, 100)}
    # pipeline1 = (toOpenCV +
    #              imp.ToBlackWhite +
    #              p1 +
    #              toFramework
    #              )
    #

    app = BeenocularsTogaTopToolbar("Beenoculars")
    # Common handlers
    init_event_bindings(app)
    #
    return app


if __name__ == "__main__":
    log.info("Debug main is called.")
    create_app().main_loop()
