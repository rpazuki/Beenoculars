from ..core import ProcessPassThrough as __PassThrough__  # noqa
from .processes import MaskContoursByAreaProcess as __MaskContoursByAreaProcess__
from .processes import OverlayContoursOnProcess as __OverlayContoursOnProcess__
from .processes import ToBlackWhiteProcess as __ToBlackWhiteProcess__
from .processes import ToColorProcess as __ToColorProcess__
from .processes import ToContoursProcess as __ToContoursProcess__
from .processes import ToConvexHullContoursProcess as __ToConvexHullContoursProcess__
from .processes import ToGrayProcess as __ToGrayProcess__

ToBlackWhite = __ToBlackWhiteProcess__()
ToGray = __ToGrayProcess__()
ToColor = __ToColorProcess__()
ToContours = __ToContoursProcess__()
MaskContoursByArea = __MaskContoursByAreaProcess__()
ToConvexHullContours = __ToConvexHullContoursProcess__()
OverlayContoursOn = __OverlayContoursOnProcess__()
PassThrough = __PassThrough__()
