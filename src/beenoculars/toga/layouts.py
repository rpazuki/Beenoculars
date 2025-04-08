import logging

import numpy as np
import toga
from toga.style import Pack
from toga.style.pack import CENTER, COLUMN, ROW  # type: ignore

import beenoculars.core as core
from beenoculars.config import Config, Dict
from beenoculars.core import Event, EventType, ServiceRegistry, silence_crossed_events
from beenoculars.services import OverlayContoursService as OverlayContours
from beenoculars.toga import (
    TogaComponent,
    TogaLayout,
    TogaMultiLayoutApp,
    TogaStackedLayout,
)
from beenoculars.toga.services.io import (
    CaptureByOpenCV,
    CaptureByOpenCVThread,
    CaptureByTakePhoto,
    FileOpenOpenCV,
)

log = logging.getLogger(__name__)


class ImageInputComponent(TogaComponent):
    def __init__(self, layout: TogaStackedLayout) -> None:
        super().__init__(layout, style=Pack(
            direction=ROW, alignment=CENTER, padding=1),
            children=[
                toga.Button("Open",
                            id="file_open",
                            style=Pack(padding=5)),
                toga.Button("Capture",
                            id="capture",
                            style=Pack(padding=5)),
                toga.Button("log",
                            on_press=self.show_log,
                            style=Pack(padding=5)),
        ])

    def show_log(self, widget):
        self.ml_app.show_log()  # type: ignore

    def image_loaded(self, toga_image):
        self.parent_layout.image_loaded(toga_image)  # type: ignore

    def image_loaded_as_pillow(self, image):
        toga_image = toga.Image(image)
        self.parent_layout.image_loaded(Dict(image=toga_image))  # type: ignore

    def on_linux_config(self):
        #
        ServiceRegistry().bind_event(
            Event("file_open",
                  EventType.ON_PRESS,
                  FileOpenOpenCV(),
                  service_callback=self.image_loaded)
        )
        ServiceRegistry().bind_event(
            Event("capture",
                  EventType.ON_PRESS,
                  CaptureByOpenCVThread(),
                  service_callback=self.image_loaded)
        )

    def on_darwin_config(self):
        #
        ServiceRegistry().bind_event(
            Event("file_open",
                  EventType.ON_PRESS,
                  FileOpenOpenCV(),
                  service_callback=self.image_loaded)
        )
        ServiceRegistry().bind_event(
            Event("capture",
                  EventType.ON_PRESS,
                  CaptureByTakePhoto(),
                  service_callback=self.image_loaded)
        )

    def on_ios_config(self):
        #
        from beenoculars.services.photo_picker_ios import (
            ImagePickerReturn,
            IOSPhotoPicker,
        )
        ServiceRegistry().bind_event(
            Event("file_open",
                  EventType.ON_PRESS,
                  IOSPhotoPicker(ImagePickerReturn.IMAGE),
                  service_callback=self.image_loaded_as_pillow)
        )
        ServiceRegistry().bind_event(
            Event("capture",
                  EventType.ON_PRESS,
                  CaptureByTakePhoto(),
                  service_callback=self.image_loaded)
        )

    def on_ipados_config(self):
        #
        from beenoculars.services.photo_picker_ios import (
            ImagePickerReturn,
            IOSPhotoPicker,
        )
        ServiceRegistry().bind_event(
            Event("file_open",
                  EventType.ON_PRESS,
                  IOSPhotoPicker(ImagePickerReturn.IMAGE),
                  service_callback=self.image_loaded_as_pillow)
        )
        ServiceRegistry().bind_event(
            Event("capture",
                  EventType.ON_PRESS,
                  CaptureByTakePhoto(),
                  service_callback=self.image_loaded)
        )

    def on_windows_config(self):
        #
        ServiceRegistry().bind_event(
            Event("file_open",
                  EventType.ON_PRESS,
                  FileOpenOpenCV(),
                  service_callback=self.image_loaded)
        )
        ServiceRegistry().bind_event(
            Event("capture",
                  EventType.ON_PRESS,
                  CaptureByOpenCV(),
                  service_callback=self.image_loaded)
        )


class ImageViewComponent(TogaComponent):

    def __init__(self, layout: TogaStackedLayout, **kwargs) -> None:
        self._image_view = toga.ImageView(
            id="image_view", style=Pack(padding=10, flex=1))
        super().__init__(layout,
                         style=Pack(direction=ROW, alignment=CENTER,
                                    padding=1, flex=1),
                         children=[
                             self._image_view,
                         ])

    @property
    def image_view(self) -> toga.ImageView:
        return self._image_view


class OverlayComponent(TogaComponent):
    def __init__(self, layout: TogaStackedLayout, **kwargs) -> None:
        super().__init__(layout, style=Pack(direction=COLUMN,
                                            alignment=CENTER))
        self.add(self._create_toolbar_row_1())
        self.add(self._create_toolbar_row_2())
        self.add(self._create_toolbar_row_3())

    def _create_toolbar_row_1(self):
        toolbar_r1 = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, padding=1))
        #

        def swt_gray_on_change(widget,  *args):
            if self.swt_gray.value and self.swt_black_white.value:
                self.swt_black_white.value = False

        def swt_black_white_on_change(widget,  *args):
            if self.swt_black_white.value and self.swt_gray.value:
                self.swt_gray.value = False
        #
        self.swt_gray = toga.Switch("⬜",
                                    id="change_grey",
                                    style=Pack(width=75, padding=5),
                                    on_change=swt_gray_on_change)
        toolbar_r1.add(self.swt_gray)
        #
        self.swt_black_white = toga.Switch("☐",
                                           id="change_black_white",
                                           style=Pack(width=75, padding=5),
                                           on_change=swt_black_white_on_change)
        toolbar_r1.add(self.swt_black_white)
        #
        silence_crossed_events(EventType.ON_CHANGE,
                               self.swt_gray,  self.swt_black_white)
        #
        self.swt_contours = toga.Switch("∾",
                                        id="draw_contours",
                                        style=Pack(width=75, padding=5))
        toolbar_r1.add(self.swt_contours)
        #
        #
        s_label = toga.Label("⬪⬧⧫", style=Pack(width=50, padding=5))
        toolbar_r1.add(s_label)
        #
        self.number_thickness = toga.Selection(id="change_line_thickness",
                                               items=[1, 2, 3, 4, 5],
                                               value=4,
                                               style=Pack(width=40, padding=5))

        toolbar_r1.add(self.number_thickness)
        #
        return toolbar_r1

    def _create_toolbar_row_2(self):
        toolbar_r2 = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, padding=1))
        #
        s_label = toga.Label("≤", style=Pack(width=20))
        toolbar_r2.add(s_label)
        #
        self.slider_threshold_label = toga.Label("127", style=Pack(width=30))
        toolbar_r2.add(self.slider_threshold_label)
        #

        def update_threshold_label(widget, *args):
            self.slider_threshold_label.text = str(int(widget.value))

        self.slider_threshold_level = toga.Slider(
            value=127, min=0, max=255,
            id="change_overlay_threshold",
            # tick_count=256,
            style=Pack(padding=5, width=200),
            on_change=update_threshold_label
        )
        slider_box = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, width=200, padding=5, flex=1))
        slider_box.add(self.slider_threshold_level)
        toolbar_r2.add(slider_box)
        #
        s_label = toga.Label("#", style=Pack(width=5, padding=10))
        toolbar_r2.add(s_label)
        #
        self.lb_count = toga.Label("", style=Pack(width=60, padding=10))
        toolbar_r2.add(self.lb_count)
        #
        return toolbar_r2

    def _create_toolbar_row_3(self):
        toolbar_r3 = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, padding=1))

        def update_percentage_label(widget, *args):
            v1 = self.slider_percentage_level_1.value
            v2 = self.slider_percentage_level_2.value
            # v1, v2 = min(v1, v2), max(v1, v2)
            self.percentage_1_label.text = f"{v1:.0f}%"
            self.percentage_2_label.text = f"{v2:.0f}%"
            # self.slider_percentage_label.text = f"{v1:.1f}-{v2:.1f}"

        sliders_box_1 = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, width=250, padding=5, flex=1))
        self.percentage_1_label = toga.Label("50%", style=Pack(width=35))
        self.slider_percentage_level_1 = toga.Slider(
            value=50, min=50, max=100,
            id="change_overlay_percentage_1",
            tick_count=200,
            style=Pack(padding=5, width=250),
            on_change=update_percentage_label
        )
        sliders_box_1.add(self.percentage_1_label,
                          self.slider_percentage_level_1)
        #
        sliders_box_2 = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, width=250, padding=5, flex=1))
        self.percentage_2_label = toga.Label("100%", style=Pack(width=35))
        self.slider_percentage_level_2 = toga.Slider(
            value=100, min=50, max=100,
            id="change_overlay_percentage_2",
            tick_count=200,
            style=Pack(padding=5, width=250),
            on_change=update_percentage_label
        )
        sliders_box_2.add(self.percentage_2_label,
                          self.slider_percentage_level_2)
        #
        sliders_box = toga.Box(style=Pack(
            direction=COLUMN, alignment=CENTER, width=290, padding=5, flex=1))
        sliders_box.add(sliders_box_1, sliders_box_2)
        toolbar_r3.add(sliders_box)
        #
        return toolbar_r3

    def is_gray(self):
        return self.swt_gray.value

    def is_bw(self):
        return self.swt_black_white.value

    def has_contour(self):
        return self.swt_contours.value

    def threshold(self):
        return core.int_(self.slider_threshold_level.value,
                         default=127)

    def percentages(self):
        percentage_1 = core.int_(self.slider_percentage_level_1.value,
                                 default=40)
        percentage_2 = core.int_(self.slider_percentage_level_2.value,
                                 default=60)
        percentages = (min(percentage_1, percentage_2),
                       max(percentage_1, percentage_2))
        return percentages

    def contours_thickness(self):
        return core.int_(self.number_thickness.value,
                         default=1)

    def get_original_image(self):
        return self.parent_layout.original_image  # type: ignore

    def contour_callback(self, results):
        self.parent_layout.image_view.image = results.image  # type: ignore
        if results.masks is not None:
            self.lb_count.text = f"{int(np.sum(results.masks)):2d}"

    def on_common_config(self):
        ############
        # Settings
        settings = self.ml_app.settings
        self.swt_gray.value = settings.OverlayComponent.is_gray
        self.swt_black_white.value = settings.OverlayComponent.is_bw
        self.swt_contours.value = settings.OverlayComponent.has_contour
        self.slider_threshold_level.value = settings.OverlayComponent.threshold
        self.slider_percentage_level_1.value = settings.OverlayComponent.percentages[0]
        self.slider_percentage_level_2.value = settings.OverlayComponent.percentages[1]
        self.number_thickness.value = settings.OverlayComponent.contours_thickness
        #
        registry = ServiceRegistry()
        args_dict = {
            'input_image': self.get_original_image,
            'threshold': self.threshold,
            'percentages': self.percentages,
            'contours_thickness': self.contours_thickness,
            'is_gray': self.is_gray,
            'is_bw': self.is_bw,
            'has_contour': self.has_contour,
        }

        registry.bind(id="change_grey",
                      eventType=EventType.ON_CHANGE,
                      service=OverlayContours(),
                      service_callback=self.contour_callback,
                      extra_kwargs=args_dict)
        registry.bind(id="change_black_white",
                      eventType=EventType.ON_CHANGE,
                      service=OverlayContours(),
                      service_callback=self.contour_callback,
                      extra_kwargs=args_dict)
        registry.bind(id="change_overlay_threshold",
                      eventType=EventType.ON_RELEASE,
                      service=OverlayContours(),
                      service_callback=self.contour_callback,
                      extra_kwargs=args_dict)
        registry.bind(id="change_overlay_percentage_1",
                      eventType=EventType.ON_RELEASE,
                      service=OverlayContours(),
                      service_callback=self.contour_callback,
                      extra_kwargs=args_dict)
        registry.bind(id="change_overlay_percentage_2",
                      eventType=EventType.ON_RELEASE,
                      service=OverlayContours(),
                      service_callback=self.contour_callback,
                      extra_kwargs=args_dict)
        registry.bind(id="change_line_thickness",
                      eventType=EventType.ON_CHANGE,
                      service=OverlayContours(),
                      service_callback=self.contour_callback,
                      extra_kwargs=args_dict)
        registry.bind(id="draw_contours",
                      eventType=EventType.ON_CHANGE,
                      service=OverlayContours(),
                      service_callback=self.contour_callback,
                      extra_kwargs=args_dict)

    def on_end(self):
        ############
        # Settings
        settings = self.ml_app.settings
        settings.OverlayComponent.is_gray = self.swt_gray.value
        settings.OverlayComponent.is_bw = self.swt_black_white.value
        settings.OverlayComponent.has_contour = self.swt_contours.value
        settings.OverlayComponent.threshold = self.slider_threshold_level.value
        settings.OverlayComponent.percentages = [self.slider_percentage_level_1.value,
                                                 self.slider_percentage_level_2.value]
        settings.OverlayComponent.contours_thickness = self.number_thickness.value


class TopToolbarLayout(TogaStackedLayout):
    def __init__(self, app: TogaMultiLayoutApp):
        super().__init__(app,
                         ImageInputComponent,
                         OverlayComponent,
                         ImageViewComponent)
        self._original_image = None

    @property
    def original_image(self):
        if (self._original_image is None and
            self.image_view is not None and
                self.image_view.image is not None):
            self._original_image = self.image_view.image
        return self._original_image

    @original_image.setter
    def original_image(self, value):
        self._original_image = value
        self.image_view.image = value

    @property
    def image_view(self) -> toga.ImageView:
        if self[ImageViewComponent] is None:
            raise ValueError("Main box has not been initialized.")
        return self[ImageViewComponent]._image_view

    @property
    def lb_count(self) -> toga.Label:
        return self[OverlayComponent].lb_count

    def image_loaded(self, toga_image):
        self.original_image = toga_image.image
        registry = ServiceRegistry()
        registry.fire_event("draw_contours",
                            self.ml_app)


class LogViewLayout(TogaLayout):

    def show_main(self, widget):
        self.ml_app.show_main()  # type: ignore

    def _build_box(self):
        """Construct and show the content layout of Toga application."""
        log.info("Log View startup")
        #
        #
        return toga.Box(style=Pack(flex=1,
                                   direction=COLUMN,
                                   alignment=CENTER),
                        children=[
            self._create_toolbar(),
            self._create_multiline_textbox()
        ]
        )

    def _create_toolbar(self):
        toolbar_r1 = toga.Box(style=Pack(  # background_color=("#005500"),
            direction=ROW, alignment=CENTER, padding=1))
        #
        self.btn_return = toga.Button("Return",
                                      on_press=self.show_main,
                                      style=Pack(padding=5)
                                      )
        toolbar_r1.add(self.btn_return)
        #

        def clear(widget):
            if Config.log.to_file:
                log_path = self.ml_app.paths.data / Config.log.file_name  # type: ignore
                with open(log_path, 'w') as file:
                    file.write("")
            self.output_textbox.value = ""
        self.btn_clear = toga.Button("Clear",
                                     on_press=clear,
                                     style=Pack(padding=5))
        toolbar_r1.add(self.btn_clear)
        #
        return toolbar_r1

    def _create_multiline_textbox(self):

        remaining_box = toga.Box(style=Pack(  # background_color=("#005500"),
            direction=COLUMN, alignment=CENTER, padding=1, flex=1))
        self.output_textbox = toga.MultilineTextInput(
            readonly=True, style=Pack(padding=5, flex=1))
        remaining_box.add(self.output_textbox)
        #
        return remaining_box

    def to_end(self, widget):
        self.output_textbox.scroll_to_bottom()

    def on_load(self):
        # Load the log
        if Config.log.to_file:
            log_path = self.ml_app.paths.data / Config.log.file_name  # type: ignore
            with open(log_path, 'r') as file:
                log_text = file.read()
                self.output_textbox.value = log_text
