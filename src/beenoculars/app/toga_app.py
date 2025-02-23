"""
Studying bees diseases by analysing photos
"""
import logging

from beenoculars.core.__core__ import ServiceRegistry, UIFramework
from beenoculars.toga import LayoutApp
from beenoculars.toga.layouts import TopToolbarLayout
from beenoculars.toga.py_interpreter import InterpreterLayoutApp, TwoColumnsLayout

# logger
log = logging.getLogger(__name__)


class BeenocularsTogaTopToolbar(LayoutApp):
    def __init__(self, formal_name: str):
        super().__init__(formal_name=formal_name,
                         app_id="com.beenoculars",
                         layout=TopToolbarLayout()
                         )


class InterpreterApp(InterpreterLayoutApp):
    def __init__(self, formal_name: str):
        super().__init__(formal_name=formal_name,
                         app_id="com.beenoculars",
                         layout=TwoColumnsLayout()
                         )


def create_app():
    log.info("Python Interpreter app stars")

    ServiceRegistry().ui_framework = UIFramework.TOGA
    app = InterpreterApp("PythonInterpreter")
    return app


if __name__ == "__main__":
    log.info("Debug main is called.")
    create_app().main_loop()
