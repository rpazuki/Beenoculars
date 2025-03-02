"""
Studying bees diseases by analysing photos
"""
import logging

from beenoculars.core import ServiceRegistry, UIFramework
from beenoculars.toga.py_interpreter import InterpreterLayoutApp, TwoColumnsLayout

# logger
log = logging.getLogger(__name__)


class Interpreter(InterpreterLayoutApp):
    def __init__(self, formal_name: str):
        super().__init__(formal_name=formal_name,
                         app_id="com.beenoculars",
                         layout=TwoColumnsLayout()
                         )


def create_app():
    log.info("Interpreter app stars")
    ServiceRegistry().ui_framework = UIFramework.TOGA
    app = Interpreter("Beenoculars")
    #
    return app


if __name__ == "__main__":
    log.info("Debug main is called.")
    create_app().main_loop()
