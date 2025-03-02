
import logging

from kivy.app import App  # type: ignore # as kivyApp
from kivy.core.window import Window  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore

import beenoculars.core as core
from beenoculars.core import AbstractApp, AbstractLayout

# from pathlib import Path


log = logging.getLogger(__name__)

TOOLBAR_HEIGHT = 85


# Builder.load_file(str(Path("layout.kv").resolve()))


class Layout(AbstractLayout):
    def __init__(self):
        super(Layout, self).__init__()
        self._main_box = None

    @property
    def main_box(self):
        if self._main_box is None:
            raise ValueError("Main box has not been initialized.")
        return self._main_box

    @property
    def picture(self):
        return self.main_box.picture

    @property
    def ids(self):
        return self.main_box.ids

    def build_layout(self):
        self._main_box = BoxLayoutApp()
        return self._main_box

    # def open(self):
    #     path = filechooser.open_file(title="Pick an image file..",
    #                                  # filters=[("Comma-separated Values", "*.csv")]
    #                                  )
    #     log.info(path)
    #     if path and len(path) > 0:
    #         self.load_image_from_path(path[0])

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


class BoxLayoutApp(BoxLayout):
    def __init__(self, **kwargs):
        super(BoxLayoutApp, self).__init__(**kwargs)
        # setattr(self.ids["'Open'"], "id", "Open",)
        for key in self.ids:
            setattr(self.ids[key], "id", key)
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
        self.picture = PictureLayout()
        self.add_widget(self.picture)
        # o = self.ids['file_open_cv']
        # o.on_press = self.test

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


class PictureLayout(BoxLayout):

    # source = StringProperty(None)
    def __init__(self, **kwargs):
        super(PictureLayout, self).__init__(**kwargs)
        self.image = self.ids.image  # self.children[0].children[0]
        self.set_image_size()

    def set_image_size(self):
        self.image_width, self.image_height = self.image.texture_size[
            0], self.image.texture_size[1]

    def reset_image_position_and_size(self):
        window_width, window_height = Window.size[0], Window.size[1]
        window_height -= TOOLBAR_HEIGHT  # subtract the height of the toolbar
        image_width, image_height = self.image_width, self.image_height

        if image_width > window_width:
            new_image_width, new_image_height = window_width, window_width / self.image.image_ratio
        elif image_height > window_height:
            new_image_width, new_image_height = window_height * \
                self.image.image_ratio, window_height
        else:
            new_image_width, new_image_height = image_width, image_height

        if new_image_height > window_height:
            new_image_width, new_image_height = window_height * \
                self.image.image_ratio, window_height

        self.image.size = (new_image_width, new_image_height)
        self.image.center = (
            Window.center[0], Window.center[1] - TOOLBAR_HEIGHT / 2)


class KivyLayoutApp(AbstractApp, App):
    def __init__(self, layout: Layout, **kwargs):
        super(KivyLayoutApp, self).__init__(
            layout=layout,
            **kwargs)
        self.layout = layout
        self._original_image = None

    @property
    def original_image(self):
        if (self._original_image is None and
            self.layout.picture is not None and
                self.layout.picture.image is not None):
            self._original_image = self.layout.picture.image.texture
        return self._original_image

    @original_image.setter
    def original_image(self, value):
        self._original_image = value
        self.layout.picture.image.texture = value
        self.layout.picture.set_image_size()
        self.layout.picture.reset_image_position_and_size()

    def load_image_from_path(self, path):
        self.layout.picture.image.source = path
        self._original_image = self.layout.picture.image.texture
        self.layout.picture.set_image_size()
        self.layout.picture.reset_image_position_and_size()

    def build(self):
        # layout = BoxLayoutApp()
        self.on_begin()
        return self.layout.main_box

    def on_stop(self):
        self.on_end()
        return super().on_stop()
