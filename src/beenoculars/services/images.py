import logging
from typing import Any

import beenoculars.core as core
import beenoculars.image_processing as imp
from beenoculars.config import Dict
from beenoculars.core import ServiceCallback, processFactory, processLogicProperty
from beenoculars.core.__image_services__ import SyncImageService
from beenoculars.image_processing.edge_detections import triple_choice_background

log = logging.getLogger(__name__)


class OverlayContoursService(SyncImageService):

    #########################################################
    # Define te pipelines logic
    #########################################################
    # An example of processLogicProperty: it defines the logic
    # of the pipeline based on the parameters, it impliment
    # the process method of the pipeline

    @processLogicProperty
    def contoursMasksPipeline(self,
                              contours,
                              masks,
                              **kwargs) -> Dict:
        selected_contours = tuple(
            c for c, mask in zip(contours, masks) if mask)
        return Dict(contours=selected_contours)

    # An example of processFactory: it creates a pipline based on the
    # parameters
    @processFactory(cache=True)
    def createPipeline(self, is_gray: bool, is_bw: bool, has_contour: bool):
        pl_background = triple_choice_background(is_gray, is_bw)
        if not has_contour:
            return pl_background >> self.toFramework

        pl_counters = (imp.ToBlackWhite >>
                       imp.ToContours >>
                       imp.ToConvexHullContours >>
                       imp.MaskContoursByArea >>
                       self.contoursMasksPipeline
                       )
        ####################################################################
        #                      pl_counters
        #                  /                \(counters)
        #  pl_background >>                  >>>>>>>>>>>>> OverlayContoursOn
        #                  \                /(backgound)
        #                    imp.PassThrough
        #####################################################################
        pipline = (pl_background >>
                   (pl_counters * imp.PassThrough) >>
                   imp.OverlayContoursOn >>
                   self.toFramework)

        return pipline

    counter = 0

    @core.safe_call(log)
    def handle_event(self,
                     widget: Any,
                     app: core.AbstractApp,
                     service_callback: ServiceCallback | None,
                     input_image,
                     threshold: int = 127,
                     percentages=(40, 100),
                     contours_thickness=5,
                     is_gray=False,
                     is_bw=False,
                     has_contour=False,
                     *args,
                     **kwargs):
        #########################################################
        # Parametrise the pipelines
        #########################################################
        pipeline = self.createPipeline(is_gray=is_gray,
                                       is_bw=is_bw,
                                       has_contour=has_contour)
        #########################################################
        # Run the pipeline
        #########################################################
        # If there is no image, do nothing
        if input_image is None:
            return
        #########################################################
        # Initilise the pipline based on user's settings
        init_params = Dict(image=input_image,
                           threshold=threshold,
                           has_contour=has_contour,
                           percentages=percentages,
                           contours_thickness=contours_thickness,
                           contours_color=(0, 0, 255),)
        #########################################################
        # Run the pipeline
        results = pipeline(**init_params)
        #########################################################
        # If the contours are searched, call the callback
        if service_callback is not None:
            service_callback(results)
