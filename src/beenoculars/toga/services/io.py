import logging
from time import sleep
from typing import Any

import toga
from toga import Widget

import beenoculars.core as core
from beenoculars.config import Dict
from beenoculars.core import ServiceCallback, safe_async_call, safe_call
from beenoculars.toga.image_processing import ToTogaImage

log = logging.getLogger(__name__)


class FileOpenOpenCV(core.AsyncService):
    def __init__(self) -> None:
        super().__init__()
        self.toTogaImage = ToTogaImage()

    @safe_async_call(log)
    async def handle_event(self,
                           widget: Any,
                           app,
                           service_callback: ServiceCallback | None,
                           *args, **kwargs):
        import cv2
        fname = await widget.app.dialog(toga.OpenFileDialog("Open file with Toga"))
        if fname is None:
            return  # No file selected
        # Load and convert the image to a texture
        frame = cv2.imread(str(fname))
        toga_image: Dict = self.toTogaImage(image=frame)
        if service_callback is not None:
            service_callback(toga_image)
        return


class CaptureByTakePhoto(core.AsyncService):
    def __init__(self) -> None:
        super().__init__()
        self.toTogaImage = ToTogaImage()

    @safe_async_call(log,
                     {NotImplementedError: "The Camera API is not implemented on this platform.",
                      PermissionError: "You have not granted permission to take photos.", }
                     )
    async def handle_event(self,
                           widget: Widget,
                           app,
                           service_callback: ServiceCallback | None,
                           *args,
                           **kwargs):
        if not app.camera.has_permission:  # type: ignore
            await app.camera.request_permission()  # type: ignore
        toga_image = await app.camera.take_photo()  # type: ignore
        if toga_image:
            if service_callback is not None:
                service_callback(Dict(image=toga_image))
        else:
            log.error(" Cannot capture photo.")


class CaptureByOpenCV(core.SyncService):
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
    def handle_event(self,
                     widget: Any,
                     app,
                     service_callback: ServiceCallback | None,
                     *args,
                     **kwargs):
        success, frame = self.capture.read()
        counter = 0
        while not success and counter < 20:
            sleep(0.1)
            success, frame = self.capture.read()
            counter += 1
        if success:
            toga_image: Dict = self.toTogaImage(image=frame)
            if service_callback is not None:
                service_callback(toga_image)
        else:
            log.error("CaptureByOpenCV: Cannot capture photo.")

    def on_exit(self):
        if self.capture is not None:
            self.capture.release()


class CaptureByOpenCVThread(core.SyncService):
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
    def handle_event(self,
                     widget: Any,
                     app,
                     service_callback: ServiceCallback | None,
                     *args,
                     **kwargs):
        from beenoculars.camera_thread import CaptureThreadGlobals
        frame = CaptureThreadGlobals.frame
        counter = 0
        while frame is None and counter < 20:
            sleep(0.1)
            frame = CaptureThreadGlobals.frame
            counter += 1
        if frame is not None:
            toga_image: Dict = self.toTogaImage(image=frame)
            if service_callback is not None:
                service_callback(toga_image)
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
