
import logging

import numpy as np

from beenoculars.services import OverlayContoursService

log = logging.getLogger(__name__)


class KivyOverlayContours(OverlayContoursService):
    def _get_original_image(self, app):
        return app.original_image

    def _set_image(self, app, image):
        app.layout.picture.image.texture = image

    def _contour_callback(self, widget, app, contours, hierarchy, areas, masks):
        app.layout.ids.lb_count.text = f"Count:{int(np.sum(masks)):2d}"
