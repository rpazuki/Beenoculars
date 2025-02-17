import logging
from time import sleep
from typing import Any

import toga
from toga import Widget

import beenoculars.core as core
from beenoculars.core import safe_async_call, safe_call
from beenoculars.toga import LayoutApp
from beenoculars.toga.image_processing import ToTogaImageProcess
from beenoculars.toga.image_processing import ToTogaImageProcess as ToTogaImage

log = logging.getLogger(__name__)


class FileOpenOpenCV(core.AsyncServiceStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.toTogaImage = ToTogaImageProcess()

    @safe_async_call(log)
    async def handle_event(self, widget: Any, app: core.AbstractApp, *args, **kwargs):
        import cv2
        fname = await widget.app.dialog(toga.OpenFileDialog("Open file with Toga"))
        if fname is None:
            return  # No file selected
        # Load and convert the image to a texture
        frame = cv2.imread(str(fname))
        image = self.toTogaImage(frame)
        app.original_image = image
        return


class CaptureByTakePhoto(core.AsyncServiceStrategy):
    @safe_async_call(log,
                     {NotImplementedError: "The Camera API is not implemented on this platform.",
                      PermissionError: "You have not granted permission to take photos.", }
                     )
    async def handle_event(self, widget: Widget, app: LayoutApp, *args, **kwargs):
        if not app.camera.has_permission:
            await app.camera.request_permission()
        image = await app.camera.take_photo()
        if image:
            app.original_image = image
        else:
            log.error(" Cannot capture photo.")


class CaptureByOpenCV(core.SyncServiceStrategy):
    def __init__(self):
        super().__init__()
        import cv2

        try:
            self.toTogaImage = ToTogaImage()
            self.__capture = cv2.VideoCapture(cv2.CAP_V4L2)
        except Exception as e:
            log.error(f"CaptureByOpenCV: {e}")

    @property
    def capture(self):
        return self.__capture

    @safe_call(log)
    def handle_event(self, widget: Any, app: core.AbstractApp, *args, **kwargs):
        success, frame = self.capture.read()
        counter = 0
        while not success and counter < 20:
            sleep(0.1)
            success, frame = self.capture.read()
            counter += 1
        if success:
            image = self.toTogaImage(frame)
            app.original_image = image
        else:
            log.error("CaptureByOpenCV: Cannot capture photo.")

    def on_exit(self):
        if self.capture is not None:
            self.capture.release()


class CaptureByOpenCVThread(core.SyncServiceStrategy):
    @safe_call(log)
    def __init__(self):
        super().__init__()
        import cv2

        from beenoculars.camera_thread import CaptureThread
        self.toTogaImage = ToTogaImage()
        self.__capture = cv2.VideoCapture(cv2.CAP_V4L2)
        self.__thread = CaptureThread(self.__capture)
        self.__thread.start()

    @safe_call(log)
    def handle_event(self, widget: Any, app: core.AbstractApp, *args, **kwargs):
        from beenoculars.camera_thread import CaptureThreadGlobals

        frame = CaptureThreadGlobals.frame
        counter = 0
        while frame is None and counter < 20:
            sleep(0.1)
            frame = CaptureThreadGlobals.frame
            counter += 1
        if frame is not None:
            image = self.toTogaImage(frame)
            app.original_image = image
        else:
            log.error("CaptureByOpenCVThread: Cannot capture photo.")

    def on_exit(self):
        from beenoculars.camera_thread import CaptureThreadGlobals

        CaptureThreadGlobals.stop = True
        counter = 0
        while self.__thread.is_alive() and counter < 20:
            sleep(0.1)
            CaptureThreadGlobals.stop = True
            counter += 1
        if self.__thread.is_alive():
            log.error("Canot close video capture thread.")
        if self.__capture is not None:
            self.__capture.release()
