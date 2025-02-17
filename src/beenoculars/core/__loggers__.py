import logging
import os

is_not_kivy = True
try:
    from kivy.logger import Logger
    logging.root = Logger
    is_not_kivy = False
except ImportError:
    pass


class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        return repr(result)

    def format(self, record):
        result = super().format(record)
        if record.exc_text:
            result = result.replace("\n", "")
        return result


handler = logging.StreamHandler()
LOGGER_FORMAT = logging.BASIC_FORMAT
# LOGGER_FORMAT = "%(levelname)s:%(name)s:%(message)s \n %(pathname)s @ %(lineno)d"
# LOGGER_FORMAT = "%(levelname)s:%(name)s:%(message)s (in %(filename)s @ line %(lineno)d)"
formatter = OneLineExceptionFormatter(LOGGER_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
if is_not_kivy:
    root.addHandler(handler)


# log = logging.getLogger(__name__)


def __dummy__():
    pass
