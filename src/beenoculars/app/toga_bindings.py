
import platform

from beenoculars.core import Event, EventType, ServiceRegistry
from beenoculars.toga.services import TogaOverlayContours  # BWAndColor, GrayAndColor,
from beenoculars.toga.services.io import (
    CaptureByOpenCV,
    CaptureByOpenCVThread,
    CaptureByTakePhoto,
    FileOpenOpenCV,
)


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
                              EventType.ON_RELEASE,
                              TogaOverlayContours(),
                              extra_kwargs=args_dict))
    registry.bind_event(Event("change_overlay_percentage_1",
                              EventType.ON_RELEASE,
                              TogaOverlayContours(),
                              extra_kwargs=args_dict))
    registry.bind_event(Event("change_overlay_percentage_2",
                              EventType.ON_RELEASE,
                              TogaOverlayContours(),
                              extra_kwargs=args_dict))
    registry.bind_event(Event("change_line_thickness",
                              EventType.ON_CHANGE,
                              TogaOverlayContours(),
                              extra_kwargs=args_dict))
    registry.bind_event(Event("change_grey",
                              EventType.ON_CHANGE,
                              TogaOverlayContours(),
                              extra_kwargs=args_dict))
    registry.bind_event(Event("change_black_white",
                              EventType.ON_CHANGE,
                              TogaOverlayContours(),
                              extra_kwargs=args_dict))
    registry.bind_event(Event("draw_contours",
                              EventType.ON_CHANGE,
                              TogaOverlayContours(),
                              extra_kwargs=args_dict))


def linux_bindings(app):
    ServiceRegistry().bind_event(
        Event("capture", EventType.ON_PRESS, CaptureByOpenCVThread())
    )


def darwin_bindings(app):
    ServiceRegistry().bind_event(
        Event("capture", EventType.ON_PRESS, CaptureByTakePhoto())
    )


def ios_bindings(app):
    ServiceRegistry().bind_event(
        Event("capture", EventType.ON_PRESS, CaptureByTakePhoto())
    )


def ipados_bindings(app):
    ServiceRegistry().bind_event(
        Event("capture", EventType.ON_PRESS, CaptureByTakePhoto())
    )


def windows_bindings(app):
    ServiceRegistry().bind_event(
        Event("capture", EventType.ON_PRESS, CaptureByOpenCV())
    )


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
        case "ipados":
            ipados_bindings(app)
        case "windows":
            windows_bindings(app)
        case _:
            others_bindings(app)
