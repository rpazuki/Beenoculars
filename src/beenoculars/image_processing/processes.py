
import cv2 as cv
import numpy as np
from numpy import ndarray

from beenoculars.config import Dict
from beenoculars.core import Process


class ToGrayProcess(Process):
    def __call__(self, *, image: ndarray, **kwargs) -> Dict:
        return Dict(image=cv.cvtColor(image, cv.COLOR_BGR2GRAY))


class ToColorProcess(Process):
    def __call__(self, *, image: ndarray, **kwargs) -> Dict:
        return Dict(image=cv.cvtColor(image, cv.COLOR_GRAY2BGR))


class ToBlackWhiteProcess(Process):
    def __call__(self,
                 *,
                 image: ndarray,
                 threshold: int = 127,
                 **kwargs) -> Dict:
        image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        _, thresh_image = cv.threshold(
            image, threshold, 255, cv.THRESH_BINARY)
        return Dict(image=thresh_image)


class ToContoursProcess(Process):
    def __call__(self,
                 *,
                 image: ndarray,
                 **kwargs) -> Dict:
        contours, hierarchy = cv.findContours(image,
                                              cv.RETR_TREE,
                                              cv.CHAIN_APPROX_SIMPLE)
        return Dict(contours=contours, hierarchy=hierarchy)


class MaskContoursByAreaProcess(Process):
    def __call__(self,
                 *,
                 contours: list,
                 percentages=(40, 60),
                 **kwargs) -> Dict:

        areas = np.array([cv.contourArea(cnt) for cnt in contours])
        if len(areas) == 0:
            return Dict(areas=areas, masks=())
        # max_areas = np.max(areas)
        # min_areas = np.min(areas)
        # bar = (max_areas - min_areas) * percentage
        bar_1 = np.percentile(areas, percentages[0])
        bar_2 = np.percentile(areas, percentages[1])
        masks = np.where((areas > bar_1) & (areas < bar_2), True, False)
        return Dict(areas=areas, masks=masks)


class ToConvexHullContoursProcess(Process):
    def __call__(self,
                 *,
                 contours: list,
                 **kwargs) -> Dict:
        return Dict(contours=[cv.convexHull(cnt) for cnt in contours])


class OverlayContoursOnProcess(Process):
    def __call__(self,
                 *,
                 image: ndarray,
                 contours: list,
                 contours_thickness: int = 1,
                 contours_color=(0, 255, 0),
                 **kwargs) -> Dict:
        overlay_image = cv.drawContours(image, contours,
                                        contourIdx=-1,
                                        color=contours_color,
                                        thickness=contours_thickness)
        return Dict(image=overlay_image)
