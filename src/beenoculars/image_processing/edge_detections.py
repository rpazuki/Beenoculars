
import beenoculars.image_processing as imp
from beenoculars.image_processing import ToBlackWhite, ToColor, ToGray, processLogic

registry = imp.ProcessesRegistry()

# backgroundStep = (
#     registry[imp.ToOpenCVImageProcess] /
#     ((registry[imp.ToOpenCVImageProcess] + ToGray + ToColor),
#      (registry[imp.ToOpenCVImageProcess] + ToBlackWhite + ToColor))
# )


@processLogic
def backgroundProcess(is_gray: bool, is_bw: bool):
    if is_gray:
        return registry[imp.ToOpenCVImageProcess] + ToGray + ToColor
    elif is_bw:
        return registry[imp.ToOpenCVImageProcess] + ToBlackWhite + ToColor
    else:
        return registry[imp.ToOpenCVImageProcess]
