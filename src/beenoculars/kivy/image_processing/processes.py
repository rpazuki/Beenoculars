import logging

import cv2 as cv
from kivy.graphics.texture import Texture  # type: ignore
from numpy import asarray, ndarray
from PIL import Image as PILImage

from beenoculars.config import Dict
from beenoculars.core import Process, safe_call

# logger
log = logging.getLogger(__name__)


def to_texture(frame, flip_x=False, flip_y=False):
    """Converts a given frame to a texture.

    Parameters
    ----------
    frame : numpy.ndarray
        The input frame to be converted.
    flip_x : bool, optional
        If True, the frame will be flipped. Defaults to False.
    flip_y : bool, optional
        If True, the frame will be flipped. Defaults to False.

    Returns
    -------
    kivy.graphics.texture.Texture
        The resulting texture created from the frame.
   """
    if flip_x and flip_y:
        buf = cv.flip(frame, -1)
    elif flip_x:   # flip horizontally
        buf = cv.flip(frame, 0)
    elif flip_y:   # flip vertically
        buf = cv.flip(frame, 1)
    else:
        buf = frame
    buf = buf.tobytes()
    image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]),
                                   colorfmt='rgb')
    image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
    return image_texture


class ToOpenCVImageProcess(Process):
    @safe_call(log)
    def __call__(self, image: Texture, **kwargs) -> Dict:
        """Converts a given toga Image to a numpy array (opencv) Image.

        Parameters
        ----------
        image : kivy.graphics.texture.Texture
            A toga Image.

        Returns
        -------
        ndarray
            The resulting toga numpy array (opencv) Image.
        """
        image = PILImage.frombytes("RGBA",  # image.colorfmt.upper(),
                                   image.size,
                                   image.pixels)

        # image = PILImage.open(io.BytesIO(image.pixels))
        image = asarray(image, dtype='uint8')
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        return Dict(image=image)


class ToKivyImageProcess(Process):
    def __call__(self,
                 image: ndarray,
                 flip_x=False,
                 flip_y=False,
                 **kwargs) -> Dict:
        """Converts a given numpy array (opencv) to a toga Image.

        Parameters
        ----------
        frame : numpy.ndarray
            The input frame to be converted.
        flip_x : bool, optional
            If True, the frame will be flipped. Defaults to False.
        flip_y : bool, optional
            If True, the frame will be flipped. Defaults to False.

        Returns
        -------
        kivy.graphics.texture.Texture
            The resulting kivy Image.
        """
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        return Dict(image=to_texture(image, flip_x, flip_y))
