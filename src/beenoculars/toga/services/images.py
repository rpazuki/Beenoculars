import logging

import numpy as np

from beenoculars.services import OverlayContoursService

log = logging.getLogger(__name__)


class TogaOverlayContours(OverlayContoursService):
    def _get_original_image(self, app):
        return app.original_image

    def _set_image(self, app, image):
        app.layout.image_view.image = image

    def _contour_callback(self, widget, app, contours, areas, masks):
        app.layout.lb_count.text = f"{int(np.sum(masks)):2d}"
