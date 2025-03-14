
import logging

# from beenoculars.app.interpreter_app import create_app as create_interpreter_app
from beenoculars.toga.app import create_app as create_toga_app

log = logging.getLogger(__name__)

if __name__ == "__main__":
    log.info("main is called.")
    create_toga_app().main_loop()
