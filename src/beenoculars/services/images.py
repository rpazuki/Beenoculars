import logging
from typing import Any

import beenoculars.core as core
import beenoculars.image_processing as imp
from beenoculars.image_processing.edge_detections import backgroundProcess
from beenoculars.image_processing.pipelines import processLogic

log = logging.getLogger(__name__)


class OverlayContoursService(imp.SyncImageService):
    def __init__(self) -> None:
        super(OverlayContoursService, self).__init__()
        #
        # p2 = imp.OverlayContours @ {'selected_qs': (1, 100), }
        self.pipeline = (self.toOpenCV +
                         imp.ToBlackWhite +
                         imp.OverlayContours +
                         self.toFramework
                         )
        self.backgroundStep = backgroundProcess

    def _contour_callback(self, contours, hierarchy, areas, masks):
        pass
    #########################################################
    # Define te pipelines logic
    #########################################################

    @processLogic
    def backgroundPipeline(self, is_gray: bool, is_bw: bool):
        if is_gray:
            return self.toOpenCV + imp.ToGray + imp.ToColor
        elif is_bw:
            return self.toOpenCV + imp.ToBlackWhite + imp.ToColor
        else:
            return self.toOpenCV

    @processLogic
    def mainImagePipeline(self):
        return (self.toOpenCV +
                imp.ToBlackWhite)

    @processLogic
    def overlayPipeline(self, has_contour):
        if has_contour:
            return (imp.OverlayContours +
                    self.toFramework)
        else:
            return self.toFramework

    @core.safe_call(log)
    def handle_event(self,
                     widget: Any,
                     app: core.AbstractApp,
                     threshold: int,
                     percentages,
                     contours_thickness,
                     is_gray,
                     is_bw,
                     has_contour,
                     *args,
                     **kwargs):
        def analysis_contour_callback(contours, hierarchy, areas, masks):
            self._contour_callback(widget,
                                   app,
                                   contours,
                                   hierarchy,
                                   areas,
                                   masks)
        #########################################################
        # Parametrise the pipelines
        #########################################################
        plBackground = self.backgroundPipeline(is_gray=is_gray, is_bw=is_bw)
        plMainImage = self.mainImagePipeline()
        plOverlay = self.overlayPipeline(has_contour=has_contour)
        #########################################################
        # Join the pipelines
        #########################################################
        #
        #
        #   /-plBackground-\  background
        # --                ----------------plOverlay---
        #   \-plMainImage--/  image
        #
        #

        pipeline = (plBackground * plMainImage)
        pipeline /= {"background": 0, "image": 1}
        pipeline += plOverlay
        #########################################################
        # Run the pipeline
        #########################################################
        input_image = self._get_original_image(app)
        processed_image = pipeline(input_image,
                                   threshold=threshold,
                                   contours_thickness=contours_thickness,
                                   original_image=None,
                                   selected_qs=percentages,
                                   flip_x=False,
                                   flip_y=False,
                                   callback=analysis_contour_callback,
                                   )
        #########################################################
        # #
        # if is_gray:
        #     # Must be Gray, but needs the coloured
        #     # contours, so, truns back the channels
        #     # to three, after making it Gray
        #     background = (imp.ToGray + imp.ToColor)(background)
        # if is_bw:
        #     # Must be B&W, but needs the coloured
        #     # contours, so, truns back the channels
        #     # to three, after making it Gray
        #     background = (imp.ToBlackWhite +
        #                   imp.ToColor)(background, threshold=threshold)
        # if has_contour:
        #     def analysis_contour_callback(contours, hierarchy, areas, masks):
        #         self._contour_callback(widget,
        #                                app,
        #                                contours,
        #                                hierarchy,
        #                                areas,
        #                                masks)
        #     processed_image = self.pipeline(input_image,
        #                                     threshold=threshold,
        #                                     contours_thickness=contours_thickness,
        #                                     original_image=background,
        #                                     selected_qs=percentages,
        #                                     flip_x=False,
        #                                     flip_y=False,
        #                                     callback=analysis_contour_callback,
        #                                     )
        # else:
        #     processed_image = self.toFramework(background,
        #                                        flip_x=False,
        #                                        flip_y=False,)
        #
        self._set_image(app, processed_image)


class OverlayContoursService2(imp.SyncImageService):
    def __init__(self) -> None:
        super(OverlayContoursService, self).__init__()
        #
        # p2 = imp.OverlayContours @ {'selected_qs': (1, 100), }
        self.pipeline = (self.toOpenCV +
                         imp.ToBlackWhite +
                         imp.OverlayContours +
                         self.toFramework
                         )

    def _contour_callback(self, widget, app, contours, hierarchy, areas, masks):
        pass

    @core.safe_call(log)
    def handle_event(self,
                     widget: Any,
                     app: core.AbstractApp,
                     threshold: int,
                     percentages,
                     contours_thickness,
                     is_gray,
                     is_bw,
                     has_contour,
                     *args,
                     **kwargs):
        input_image = self._get_original_image(app)
        # processed_image = self.toOpenCV(input_image)
        # background = copy.copy(processed_image)
        # input_image = self.toOpenCV(input_image)
        background = self.toOpenCV(input_image)
        #
        if is_gray:
            # Must be Gray, but needs the coloured
            # contours, so, truns back the channels
            # to three, after making it Gray
            background = imp.ToGray(background)
            background = imp.ToColor(background)
        if is_bw:
            # Must be B&W, but needs the coloured
            # contours, so, truns back the channels
            # to three, after making it Gray
            background = imp.ToBlackWhite(background, threshold=threshold)
            background = imp.ToColor(background)
        if has_contour:
            def analysis_contour_callback(contours, hierarchy, areas, masks):
                self._contour_callback(widget,
                                       app,
                                       contours,
                                       hierarchy,
                                       areas,
                                       masks)
            processed_image = self.pipeline(input_image,
                                            threshold=threshold,
                                            contours_thickness=contours_thickness,
                                            original_image=background,
                                            selected_qs=percentages,
                                            flip_x=False,
                                            flip_y=False,
                                            callback=analysis_contour_callback,
                                            )
        else:
            processed_image = self.toFramework(background,
                                               flip_x=False,
                                               flip_y=False,)
        #
        self._set_image(app, processed_image)


class GrayAndColor(imp.SyncImageService):
    def __init__(self) -> None:
        super(GrayAndColor, self).__init__()
        self.ToGrayPipeline = (self.toOpenCV +
                               imp.ToGray +
                               self.toFramework)

    @core.safe_call(log)
    def handle_event(self, widget: Any, app: core.AbstractApp, *args, **kwargs):
        input_image = self._get_original_image(app)
        if app.layout.swt_gray.value:  # Must be Gray
            processed_image = self.ToGrayPipeline(input_image)
        else:  # Must be Coloured
            processed_image = input_image
        self._set_image(app, processed_image)


class BWAndColor(imp.SyncImageService):
    def __init__(self) -> None:
        super(BWAndColor, self).__init__()
        self.ToBWPipeline = (self.toOpenCV +
                             imp.ToBlackWhite +
                             self.toFramework)

    @core.safe_call(log)
    def handle_event(self, widget: Any, app: core.AbstractApp, *args, **kwargs):
        input_image = self._get_original_image(app)
        if app.layout.swt_black_white.value:  # Must be B&W
            threshold = core.int_(app.layout.slider_threshold_level.value,
                                  default=127)
            processed_image = self.ToBWPipeline(input_image,
                                                threshold=threshold)
        else:  # Must be Coloured
            processed_image = input_image
        self._set_image(app, processed_image)
