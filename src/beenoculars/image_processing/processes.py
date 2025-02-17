

from typing import Any

import cv2 as cv
import numpy as np
from numpy import ndarray

from beenoculars.image_processing import Process


class ProcessesRegistry(object):
    """A singleton object that store Framework specific Process.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProcessesRegistry, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance
    processes = {}

    def __getitem__(self, key):
        return self.processes[key]

    def __setitem__(self, key, newvalue):
        self.processes[key] = newvalue


def analysis_contour_areas(contours, percentages=(40, 60)):
    areas = np.array([cv.contourArea(cnt) for cnt in contours])
    # max_areas = np.max(areas)
    # min_areas = np.min(areas)
    # bar = (max_areas - min_areas) * percentage
    bar_1 = np.percentile(areas, percentages[0])
    bar_2 = np.percentile(areas, percentages[1])
    return areas, np.where((areas > bar_1) & (areas < bar_2), True, False)


class ToOpenCVImageProcess(Process):
    def __call__(self, image: ndarray) -> Any:
        pass


class ToFrameworkImageProcess(Process):
    def __call__(self, image: Any) -> ndarray:
        pass


class ToGrayProcess(Process):
    def __call__(self, image: ndarray, /, **kwargs) -> ndarray:
        return cv.cvtColor(image, cv.COLOR_BGR2GRAY)


class ToColorProcess(Process):
    def __call__(self, image: ndarray, /, **kwargs) -> ndarray:
        return cv.cvtColor(image, cv.COLOR_GRAY2BGR)


class ToBlackWhiteProcess(Process):
    def __call__(self,
                 image: ndarray,
                 threshold: int = 127,
                 **kwargs) -> ndarray:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        _, thresh_image = cv.threshold(
            image, threshold, 255, cv.THRESH_BINARY)
        return thresh_image


class OverlayContoursProcess(Process):
    def __call__(self,
                 image: ndarray,
                 original_image: ndarray = None,
                 contours_thickness: int = 1,
                 selected_qs=(40, 60),
                 contours_color=(0, 255, 0),
                 contours_selected_color=(0, 0, 255),
                 callback=None,
                 **kwargs) -> ndarray:
        if original_image is None:
            gray_image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
            background = gray_image
        else:
            background = original_image

        contours, hierarchy = cv.findContours(image,
                                              cv.RETR_TREE,
                                              cv.CHAIN_APPROX_SIMPLE)
        contours = [cv.convexHull(cnt)
                    for cnt in contours]

        if len(contours) == 0:
            if callback is not None:
                callback(contours, hierarchy, (), ())
            return background

        areas, masks = analysis_contour_areas(contours, selected_qs)
        selected_contours = tuple(
            c for c, mask in zip(contours, masks) if mask)
        # not_selected_contours = tuple(
        #     c for c, mask in zip(contours, masks) if not mask)

        overlay_image = cv.drawContours(background, selected_contours,
                                        contourIdx=-1,
                                        color=contours_selected_color,
                                        thickness=contours_thickness)
        # overlay_image = cv.drawContours(overlay_image, not_selected_contours,
        #                                 contourIdx=-1,
        #                                 color=contours_color,
        #                                 thickness=contours_thickness)
        if callback is not None:
            callback(contours, hierarchy, areas, masks)

        return overlay_image


class OverlayContoursProcessOld(Process):
    def __call__(self,
                 image: ndarray,
                 original_image: ndarray = None,
                 contours_thickness: int = 1,
                 contours_color=(0, 255, 0),
                 callback=None,
                 **kwargs) -> ndarray:
        contours, hierarchy = cv.findContours(image,
                                              cv.RETR_TREE,
                                              cv.CHAIN_APPROX_SIMPLE)
        if callback is not None:
            callback(image, contours, hierarchy)

        if original_image is None:
            gray_image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
            background = gray_image
        else:
            background = original_image
        overlay_image = cv.drawContours(background, contours,
                                        contourIdx=-1,
                                        color=contours_color,
                                        thickness=contours_thickness)
        return overlay_image
