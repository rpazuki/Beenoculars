
import platform

from beenoculars.core import Event, EventType, ServiceRegistry
from beenoculars.kivy.services import KivyOverlayContours  # BWAndColor, GrayAndColor,
from beenoculars.kivy.services.io import CaptureByOpenCVThread  # CaptureByOpenCV,
from beenoculars.kivy.services.io import FileOpenOpenCV  # ,CaptureByTakePhoto


def common_binding(app):
    args_dict = {'threshold': app.layout.threshold,
                 'percentages': app.layout.percentages,
                 'contours_thickness': app.layout.contours_thickness,
                 'is_gray': app.layout.is_gray,
                 'is_bw': app.layout.is_bw,
                 'has_contour': app.layout.has_contour, }
    registry = ServiceRegistry()
    registry.bind_event(
        Event("file_open_cv", EventType.ON_PRESS, FileOpenOpenCV()))
    registry.bind_event(Event("change_overlay_threshold",
                              EventType.BIND,
                              KivyOverlayContours(),
                              property_name="value",
                              extra_kwargs=args_dict))
    registry.bind_event(Event("change_overlay_percentage_1",
                              EventType.BIND,
                              KivyOverlayContours(),
                              property_name="value",
                              extra_kwargs=args_dict))
    registry.bind_event(Event("change_overlay_percentage_2",
                              EventType.BIND,
                              KivyOverlayContours(),
                              property_name="value",
                              extra_kwargs=args_dict))
    registry.bind_event(Event("number_thickness",
                              EventType.BIND,
                              KivyOverlayContours(),
                              property_name="text",
                              extra_kwargs=args_dict))
    registry.bind_event(Event("change_grey",
                              EventType.BIND,
                              KivyOverlayContours(),
                              property_name="active",
                              extra_kwargs=args_dict))
    registry.bind_event(Event("change_black_white",
                              EventType.BIND,
                              KivyOverlayContours(),
                              property_name="active",
                              extra_kwargs=args_dict))
    registry.bind_event(Event("draw_contours",
                              EventType.BIND,
                              KivyOverlayContours(),
                              property_name="active",
                              extra_kwargs=args_dict))


def linux_bindings(app):
    ServiceRegistry().bind_event(
        Event("capture", EventType.ON_PRESS, CaptureByOpenCVThread())
    )


def darwin_bindings(app):
    pass


def ios_bindings(app):
    pass


def windows_bindings(app):
    pass


def others_bindings(app):
    pass


def init_event_bindings(app):
    common_binding(app)
    os = platform.system().lower()
    match os:
        case "linux":
            linux_bindings(app)
        case "darwin":
            darwin_bindings(app)
        case "ios":
            ios_bindings(app)
        case "windows":
            windows_bindings(app)
        case _:
            others_bindings(app)
