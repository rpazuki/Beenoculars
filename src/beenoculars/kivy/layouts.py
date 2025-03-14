
import logging

import numpy as np
from kivy.core.window import Window  # type: ignore

import beenoculars.core as core
from beenoculars.config import Config
from beenoculars.core import Event, EventType, ServiceRegistry
from beenoculars.kivy import (
    KivyBox,
    KivyComponent,
    KivyLayout,
    KivyMultiLayoutApp,
    KivyStackedLayout,
)
from beenoculars.kivy.services.io import CaptureByOpenCVThread, FileOpenOpenCV
from beenoculars.services import OverlayContoursService as OverlayContours

# from pathlib import Path


log = logging.getLogger(__name__)

TOOLBAR_HEIGHT = 125


# Builder.load_file(str(Path("layout.kv").resolve()))

class ImageInputComponent(KivyComponent):

    def show_log(self):
        self.ml_app.show_log()

    def image_loaded(self, kivy_image):
        self.parent_layout.image_loaded(kivy_image)         # type: ignore

    def on_common_config(self):
        registry = ServiceRegistry()
        registry.bind_event(
            Event("file_open_cv",
                  EventType.ON_PRESS,
                  FileOpenOpenCV(),
                  service_callback=self.image_loaded))

    def on_linux_config(self):
        ServiceRegistry().bind_event(
            Event("capture",
                  EventType.ON_PRESS,
                  CaptureByOpenCVThread(),
                  service_callback=self.image_loaded))


class ImageViewComponent(KivyComponent):

    @property
    def image(self):
        return self.ids.image

    def set_image_size(self):
        self.image_width, self.image_height = self.ids.image.texture_size[
            0], self.ids.image.texture_size[1]

    def reset_image_position_and_size(self):
        window_width, window_height = Window.size[0], Window.size[1]
        window_height -= TOOLBAR_HEIGHT  # subtract the height of the toolbar
        image_width, image_height = self.image.texture.width, self.image.texture.height

        if image_width > window_width:
            new_image_width, new_image_height = window_width, window_width / \
                self.ids.image.image_ratio
        elif image_height > window_height:
            new_image_width, new_image_height = window_height * \
                self.ids.image.image_ratio, window_height
        else:
            new_image_width, new_image_height = image_width, image_height

        if new_image_height > window_height:
            new_image_width, new_image_height = window_height * \
                self.ids.image.image_ratio, window_height

        self.ids.image.size = (new_image_width, new_image_height)
        self.ids.image.center = (
            Window.center[0], Window.center[1] - TOOLBAR_HEIGHT / 2)


class OverlayComponent(KivyComponent):
    def __init__(self, layout: KivyStackedLayout,  **kwargs):
        super(OverlayComponent, self).__init__(layout, **kwargs)
        self.flg_changing = False
        self.ids.change_grey.bind(active=self.swt_gray_on_change)
        self.ids.change_black_white.bind(
            active=self.swt_black_white_on_change)
        self.ids.change_overlay_threshold.bind(
            value=self.threshold_label_change)
        self.ids.change_overlay_percentage_1.bind(
            value=self.percentage_label_change)
        self.ids.change_overlay_percentage_2.bind(
            value=self.percentage_label_change)

    def threshold_label_change(self, widget, value):
        self.ids.threshold_label.text = f"Threshold:{int(value)}"

    def percentage_label_change(self, widget, value):
        v1 = self.ids.change_overlay_percentage_1.value
        v2 = self.ids.change_overlay_percentage_2.value
        v1, v2 = min(v1, v2), max(v1, v2)
        self.ids.percentage_label.text = f"Percentage:{v1:.1f}-{v2:.1f}"

    def swt_gray_on_change(self, widget, value):
        if value:
            self.ids.change_black_white.active = False

    def swt_black_white_on_change(self, widget, value):
        if value:
            self.ids.change_grey.active = False

    def is_gray(self):
        return self.ids.change_grey.active

    def is_bw(self):
        return self.ids.change_black_white.active

    def has_contour(self):
        return self.ids.draw_contours.active

    def threshold(self):
        return core.int_(self.ids.change_overlay_threshold.value,
                         default=127)

    def percentages(self):
        percentage_1 = core.int_(self.ids.change_overlay_percentage_1.value,
                                 default=40)
        percentage_2 = core.int_(self.ids.change_overlay_percentage_2.value,
                                 default=60)
        percentages = (min(percentage_1, percentage_2),
                       max(percentage_1, percentage_2))
        return percentages

    def contours_thickness(self):
        return core.int_(self.ids.number_thickness.text,
                         default=1)

    def get_original_image(self):
        return self.parent_layout.original_image  # type: ignore

    def on_common_config(self):
        ############
        # Settings
        settings = self.ml_app.settings
        self.ids.change_grey.active = settings.OverlayComponent.is_gray
        self.ids.change_black_white.active = settings.OverlayComponent.is_bw
        self.ids.draw_contours.active = settings.OverlayComponent.has_contour
        self.ids.change_overlay_threshold.value = settings.OverlayComponent.threshold
        self.ids.change_overlay_percentage_1.value = settings.OverlayComponent.percentages[0]
        self.ids.change_overlay_percentage_2.value = settings.OverlayComponent.percentages[1]
        self.ids.number_thickness.text = str(
            settings.OverlayComponent.contours_thickness)
        #

        def _contour_callback(results):
            self.parent_layout.picture.image.texture = results.image  # type: ignore
            if results.masks is not None:
                self.ids.lb_count.text = f"Count:{int(np.sum(results.masks)):2d}"

        args_dict = {'input_image': self.get_original_image,
                     'threshold': self.threshold,
                     'percentages': self.percentages,
                     'contours_thickness': self.contours_thickness,
                     'is_gray': self.is_gray,
                     'is_bw': self.is_bw,
                     'has_contour': self.has_contour,
                     }
        registry = ServiceRegistry()
        registry.bind_event(Event("change_overlay_threshold",
                                  EventType.BIND,
                                  OverlayContours(),
                                  property_name="value",
                                  service_callback=_contour_callback,
                                  extra_kwargs=args_dict))
        registry.bind_event(Event("change_overlay_percentage_1",
                                  EventType.BIND,
                                  OverlayContours(),
                                  property_name="value",
                                  service_callback=_contour_callback,
                                  extra_kwargs=args_dict))
        registry.bind_event(Event("change_overlay_percentage_2",
                                  EventType.BIND,
                                  OverlayContours(),
                                  property_name="value",
                                  service_callback=_contour_callback,
                                  extra_kwargs=args_dict))
        registry.bind_event(Event("number_thickness",
                                  EventType.BIND,
                                  OverlayContours(),
                                  property_name="text",
                                  service_callback=_contour_callback,
                                  extra_kwargs=args_dict))
        registry.bind_event(Event("change_grey",
                                  EventType.BIND,
                                  OverlayContours(),
                                  property_name="active",
                                  service_callback=_contour_callback,
                                  extra_kwargs=args_dict))
        registry.bind_event(Event("change_black_white",
                                  EventType.BIND,
                                  OverlayContours(),
                                  property_name="active",
                                  service_callback=_contour_callback,
                                  extra_kwargs=args_dict))
        registry.bind_event(Event("draw_contours",
                                  EventType.BIND,
                                  OverlayContours(),
                                  property_name="active",
                                  service_callback=_contour_callback,
                                  extra_kwargs=args_dict))

    def on_end(self):
        ############
        # Settings
        settings = self.ml_app.settings
        settings.OverlayComponent.is_gray = self.ids.change_grey.active
        settings.OverlayComponent.is_bw = self.ids.change_black_white.active
        settings.OverlayComponent.has_contour = self.ids.draw_contours.active
        settings.OverlayComponent.threshold = self.ids.change_overlay_threshold.value
        settings.OverlayComponent.percentages = [self.ids.change_overlay_percentage_1.value,
                                                 self.ids.change_overlay_percentage_2.value]
        settings.OverlayComponent.contours_thickness = int(
            self.ids.number_thickness.text)


class TopToolbarLayout(KivyStackedLayout):
    def __init__(self, app: KivyMultiLayoutApp):
        super().__init__(app,
                         ImageInputComponent,
                         OverlayComponent,
                         ImageViewComponent)

        self._original_image = None

    @property
    def original_image(self):
        if (self._original_image is None and
            self.picture is not None and
                self.picture.image is not None):
            self._original_image = self.picture.image.texture
        return self._original_image

    @original_image.setter
    def original_image(self, value):
        self._original_image = value
        self.picture.image.texture = value
        self[ImageViewComponent].set_image_size()
        self[ImageViewComponent].reset_image_position_and_size()

    @property
    def picture(self):
        if self[ImageViewComponent] is None:
            raise ValueError("Main box has not been initialized.")
        return self[ImageViewComponent]

    def image_loaded(self, kivy_image):
        self.original_image = kivy_image.image
        registry = ServiceRegistry()
        registry.fire_event("draw_contours",
                            self.ml_app)

    def load_image_from_path(self, path):
        self.picture.image.source = path
        self._original_image = self.picture.image.texture
        self[ImageViewComponent].set_image_size()
        self[ImageViewComponent].reset_image_position_and_size()


class LogViewLayout(KivyLayout):

    def _build_box(self):
        log.info("Log View init.")
        return LogViewBox(self)

    def show_main(self, widget):
        self.ml_app.show_main()  # type: ignore

    def on_load(self):
        # Load the log
        if Config.log.to_file:
            log_path = self.ml_app.data_path / Config.log.file_name  # type: ignore
            with open(log_path, 'r') as file:
                log_text = file.read()
                self.ids.output_textbox.text = log_text


class LogViewBox(KivyBox):

    def on_size(self, box, dt):
        self.ids.output_textbox.size = (Window.size[0] - box.children[0].height,
                                        Window.size[1])

    def show_main(self):
        self.ml_app.show_main()

    def clear_log(self):
        if Config.log.to_file:
            log_path = self.ml_app.data_path / Config.log.file_name  # type: ignore
            with open(log_path, 'w') as file:
                file.write("")
        self.ids.output_textbox.text = ""
