
import beenoculars.image_processing as imp
from beenoculars.image_processing import (
    ImageProcessingPipeline,
    Process,
    processFactory,
)

registry = imp.ProcessesRegistry()


###########################################################
#
#      toOpenCV >> ToGray >> ToColor --
#    /                                  \
# >> - toOpenCV >> ToBlackWhite --------- >>
#    \                                  /
#      toOpenCV >> ---------------------
#
def triple_choice_background(is_gray: bool, is_bw: bool) -> ImageProcessingPipeline:
    toOpenCV = registry[imp.ToOpenCVImageProcess]
    if is_gray:
        pipeline = toOpenCV >> imp.ToGray >> imp.ToColor
    elif is_bw:
        pipeline = toOpenCV >> imp.ToBlackWhite >> imp.ToColor
    else:
        pipeline = toOpenCV
    return pipeline

# An example of processFactory: it creates a pipline based on the
# parameters


@processFactory(cache=True)
def overlay_pipeline(has_contour: bool,
                     contoursMasksLogic: Process | ImageProcessingPipeline
                     ) -> ImageProcessingPipeline:
    """Create an image processing pipeline to overlay and count the cotours.

    Parameters
    ----------
    has_contour : bool
        If it is true, contour overlays will be plotted on the image.
    contoursMasksLogic : Process | ImageProcessingPipeline
        The logic for filtering cotours.
        It must be a process that takes litss of contours and masks
        and returns a Dict of filtered contours.

    Returns
    -------
    ImageProcessingPipeline
        An image processing pipeline.
    """
    toFramework = registry[imp.ToFrameworkImageProcess]
    if not has_contour:
        return toFramework

    pl_counters = (imp.ToBlackWhite >>
                   imp.ToContours >>
                   imp.ToConvexHullContours >>
                   imp.MaskContoursByArea >>
                   contoursMasksLogic
                   )
    ####################################################################
    #        pl_counters
    #     /                \(counters)
    #   >>                  >>>>>>>>>>>>> OverlayContoursOn
    #     \                /(backgound)
    #      imp.PassThrough
    #####################################################################
    return ((pl_counters * imp.PassThrough) >>
            imp.OverlayContoursOn >>
            toFramework)
###########################################################
