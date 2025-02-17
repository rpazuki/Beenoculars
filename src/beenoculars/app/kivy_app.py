import logging
import os

import kivy
from kivy.lang import Builder
from kivy.logger import Logger

import beenoculars.image_processing as imp
from beenoculars.app.kivy_bindings import init_event_bindings
from beenoculars.core.__core__ import ServiceRegistry, UIFramework
from beenoculars.image_processing import ProcessesRegistry
from beenoculars.kivy import KivyLayoutApp, Layout
from beenoculars.kivy.image_processing import ToCVImageProcess, ToKivyImageProcess

logging.root = Logger

kivy.require('1.8.0')

# logger
log = logging.getLogger(__name__)


class BeenocularsKivyTopToolbar(KivyLayoutApp):
    def __init__(self, **kwargs):
        super(BeenocularsKivyTopToolbar,
              self).__init__(layout=Layout(),
                             **kwargs)


def create_app():
    log.info("Beenoculars app stars")
    registry = ProcessesRegistry()
    registry[imp.ToOpenCVImageProcess] = ToCVImageProcess()
    registry[imp.ToFrameworkImageProcess] = ToKivyImageProcess()
    ServiceRegistry().ui_framework = UIFramework.KIVY
    app = BeenocularsKivyTopToolbar()
    init_event_bindings(app)
    return app


if __name__ == '__main__':
    log.info("Debug main is called.")
    Builder.load_file(os.path.abspath(
        "beenoculars/src/beenoculars/kivy/layouts.kv"))
    log.info("KV is loaded.")
    create_app().run()
