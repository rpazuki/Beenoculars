import logging
import os

from kivy.lang import Builder  # type: ignore

from beenoculars.app.kivy_app import create_app as create_kivy_app

# logger
log = logging.getLogger(__name__)

if __name__ == '__main__':
    log.info("main is called.")
    Builder.load_file(os.path.abspath(
        "beenoculars/kivy/layouts.kv"))
    log.info("KV is loaded.")
    create_kivy_app().run()
