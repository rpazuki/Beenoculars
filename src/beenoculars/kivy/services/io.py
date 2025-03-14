import logging
import os
from time import sleep
from typing import Any, Callable

from kivy.factory import Factory  # type: ignore
from kivy.lang import Builder  # type: ignore

# import toga
from kivy.properties import ObjectProperty  # type: ignore
from kivy.uix.floatlayout import FloatLayout  # type: ignore
from kivy.uix.popup import Popup  # type: ignore

import beenoculars.core as core
from beenoculars.config import Dict
from beenoculars.core import safe_call
from beenoculars.kivy.image_processing import ToKivyImage

log = logging.getLogger(__name__)


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


Factory.register('LoadDialog', cls=LoadDialog)
Builder.load_string('''
<LoadDialog>:
    BoxLayout:
        size: root.size
        pos: root.pos
        orientation: "vertical"
        FileChooserIconView:
            id: filechooser

        BoxLayout:
            size_hint_y: None
            height: 30
            Button:
                text: "Cancel"
                on_release: root.cancel()

            Button:
                text: "Load"
                on_release: root.load(filechooser.path, filechooser.selection)
                    ''')


class FileOpenOpenCV(core.SyncService):
    def __init__(self) -> None:
        super().__init__()
        self.app = None
        self.toKivyImage = ToKivyImage()

    def dismiss_popup(self):
        self._popup.dismiss()

    @safe_call(log)
    def load(self, path, filename):
        if len(filename) > 0:
            import cv2 as cv
            frame = cv.imread(filename[0])
            kivy_image: Dict = self.toKivyImage(
                image=frame, flip_x=True, flip_y=False)
            if self.service_callback is not None:
                self.service_callback(kivy_image)
        self._popup.dismiss()

    @safe_call(log)
    def handle_event(self,
                     widget: Any,
                     app: core.AbstractApp,
                     service_callback: Callable | None = None,
                     *args,
                     **kwargs):

        self.app = app
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        content.ids['filechooser'].path = os.getcwd()
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self.service_callback = service_callback
        self._popup.open()
        return


class CaptureByOpenCVThread(core.SyncService):
    @safe_call(log)
    def __init__(self):
        super().__init__()
        import cv2 as cv

        from beenoculars.camera_thread import CaptureThread
        self.toKivyImage = ToKivyImage()
        self.__capture = cv.VideoCapture(cv.CAP_V4L2)
        self.__thread = CaptureThread(self.__capture)
        self.__thread.start()

    @safe_call(log)
    def handle_event(self,
                     widget: Any,
                     app: core.AbstractApp,
                     service_callback: Callable | None = None,
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
            kivy_image: Dict = self.toKivyImage(
                image=frame, flip_x=True, flip_y=False)
            if service_callback is not None:
                service_callback(kivy_image)
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
