import logging
from abc import abstractmethod

import toga
from toga.style import Pack
from toga.style.pack import CENTER, COLUMN, ROW

import beenoculars.core as core
from beenoculars.core import AbstractApp, AbstractLayout

log = logging.getLogger(__name__)


class Layout(AbstractLayout):
    def __init__(self):
        super(Layout, self).__init__()
        self._main_box = None
        self._image_view = None

    @property
    def main_box(self):
        return self._main_box

    @property
    def image_view(self):
        return self._image_view

    def build_layout(self):
        """Build the main window of the app and its layout.
        """
        self._main_box = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, flex=1)
        )
        #
        self._image_view = toga.ImageView(
            id="image_view", style=Pack(padding=10, flex=1))
        #
        self._build_layout(self._image_view)
        #
        return self._main_box

    @abstractmethod
    def _build_layout(self, image_view: toga.ImageView):
        """Build the layout box and all the required UI elements.

           Also, all the buttons that has an id registred in ServiceRegistry
           will be bind to on_press handlers.

        Parameters
        ----------
        image_view : toga.ImageView
            Every app have and ImageView that the layout class must
            include it in a box.
        """
        pass


class TopToolbarLayout(Layout):

    def _build_layout(self, image_view: toga.ImageView):
        """Construct and show the content layout of Toga application."""
        log.info("TopToolbar startup")
        #
        self.main_box.add(self._create_toolbar())
        self.main_box.add(self._create_image_view(image_view))
        #

    def _create_toolbar(self):
        toolbar = toga.Box(style=Pack(
            direction=COLUMN, alignment=CENTER))
        #
        toolbar.add(self._create_toolbar_row_1())
        toolbar.add(self._create_toolbar_row_2())
        toolbar.add(self._create_toolbar_row_3())
        toolbar.add(self._create_toolbar_row_4())
        #
        return toolbar

    def _create_toolbar_row_1(self):
        toolbar_r1 = toga.Box(style=Pack(  # background_color=("#005500"),
            direction=ROW, alignment=CENTER, padding=1))
        #
        #
        self.btn_open = toga.Button("Open",
                                    id="file_open_cv",
                                    style=Pack(padding=5))
        toolbar_r1.add(self.btn_open)
        #
        self.btn_capture = toga.Button("Capture",
                                       id="capture",
                                       style=Pack(padding=5)
                                       )
        toolbar_r1.add(self.btn_capture)
        #

        def swt_gray_on_change(widget,  *args):
            if self.swt_gray.value:
                self.swt_black_white.value = False
        self.swt_gray = toga.Switch("Grey:",
                                    id="change_grey",
                                    style=Pack(width=90, padding=10),
                                    on_change=swt_gray_on_change)
        toolbar_r1.add(self.swt_gray)
        #

        def swt_black_white_on_change(widget,  *args):
            if self.swt_black_white.value:
                self.swt_gray.value = False

        self.swt_black_white = toga.Switch("B&W:",
                                           id="change_black_white",
                                           style=Pack(width=90, padding=10),
                                           on_change=swt_black_white_on_change)
        toolbar_r1.add(self.swt_black_white)
        #
        self.swt_contours = toga.Switch("Contours:",
                                        id="draw_contours",
                                        style=Pack(width=130, padding=10))
        toolbar_r1.add(self.swt_contours)
        #
        return toolbar_r1

    def _create_toolbar_row_2(self):
        toolbar_r2 = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, padding=1))
        #
        s_label = toga.Label("Threshold:", style=Pack(width=100))
        toolbar_r2.add(s_label)
        #
        self.slider_threshold_label = toga.Label("127", style=Pack(width=25))
        toolbar_r2.add(self.slider_threshold_label)
        #

        def update_threshold_label(widget, *args):
            self.slider_threshold_label.text = str(int(widget.value))

        self.slider_threshold_level = toga.Slider(
            value=127, min=0, max=255,
            id="change_overlay_threshold",
            # tick_count=256,
            style=Pack(padding=5, width=290),
            on_change=update_threshold_label
        )
        slider_box = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, width=290, padding=5, flex=1))
        slider_box.add(self.slider_threshold_level)
        toolbar_r2.add(slider_box)
        #
        return toolbar_r2

    def _create_toolbar_row_3(self):
        toolbar_r3 = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, padding=1))
        #
        #
        s_label = toga.Label("Thickness:", style=Pack(width=95, padding=5))
        toolbar_r3.add(s_label)
        #
        self.number_thickness = toga.NumberInput(id="change_line_thickness",
                                                 min=1,
                                                 max=5,
                                                 step=1,
                                                 value=1)
        toolbar_r3.add(self.number_thickness)
        #
        s_label = toga.Label("Count:", style=Pack(width=60, padding=10))
        toolbar_r3.add(s_label)
        #
        self.lb_count = toga.Label("", style=Pack(width=60, padding=10))
        toolbar_r3.add(self.lb_count)
        #
        return toolbar_r3

    def _create_toolbar_row_4(self):
        toolbar_r4 = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, padding=1))
        #
        s_label = toga.Label("Percentage:", style=Pack(width=110))
        toolbar_r4.add(s_label)
        #
        self.slider_percentage_label = toga.Label(
            "90-100", style=Pack(width=25))
        toolbar_r4.add(self.slider_percentage_label)
        #

        def update_percentage_label(widget, *args):
            v1 = self.slider_percentage_level_1.value
            v2 = self.slider_percentage_level_2.value
            v1, v2 = min(v1, v2), max(v1, v2)
            self.slider_percentage_label.text = f"{v1:.1f}-{v2:.1f}"

        sliders_box = toga.Box(style=Pack(
            direction=COLUMN, alignment=CENTER, width=290, padding=5, flex=1))
        self.slider_percentage_level_1 = toga.Slider(
            value=90, min=90, max=100,
            id="change_overlay_percentage_1",
            tick_count=200,
            style=Pack(padding=5, width=290),
            on_change=update_percentage_label
        )
        self.slider_percentage_level_2 = toga.Slider(
            value=100, min=90, max=100,
            id="change_overlay_percentage_2",
            tick_count=200,
            style=Pack(padding=5, width=290),
            on_change=update_percentage_label
        )
        sliders_box.add(self.slider_percentage_level_1)
        sliders_box.add(self.slider_percentage_level_2)
        toolbar_r4.add(sliders_box)
        #
        return toolbar_r4

    def _create_image_view(self, image_view):
        image_view_box = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, padding=1, flex=1)
        )
        image_view_box.add(image_view)

        return image_view_box

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


class LayoutApp(AbstractApp, toga.App):
    """A toga App class that has a layout.

    The layout class will create UI elements and its main_box will be added
    as the app main window's content.
    """

    def __init__(self, formal_name: str, app_id: str, layout: Layout):

        super(LayoutApp, self).__init__(layout=layout,
                                        formal_name=formal_name,
                                        app_id=app_id,
                                        )
        self._original_image = None

    @property
    def image_view(self):
        return self.layout.image_view

    @property
    def original_image(self):
        if (self._original_image is None and
            self.layout.image_view is not None and
                self.layout.image_view.image is not None):
            self._original_image = self.layout.image_view.image
        return self._original_image

    @original_image.setter
    def original_image(self, value):
        self._original_image = value
        self.layout.image_view.image = value

    def startup(self):
        """Construct and show the Toga application.

        It also call the layout build and bind the serivices handlers
        to UI elements on_press call back, if their ids correspond to
        an id in ServiceRegistry.
        """
        self.main_window = toga.MainWindow(title=self.formal_name)
        #
        self.on_begin()
        #
        self.main_window.content = self.layout.main_box
        #
        self.main_window.show()

    def on_exit(self):
        self.on_end()
        return True
