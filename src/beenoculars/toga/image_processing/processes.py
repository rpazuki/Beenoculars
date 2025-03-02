
import io

import cv2 as cv
import toga
from numpy import asarray, ndarray
from PIL import Image as PILImage

from beenoculars.image_processing import Dict, Process


class ToCVImageProcess(Process):
    def __call__(self, *, image: toga.Image, **kwargs) -> Dict:
        """Converts a given toga Image to a numpy array (opencv) Image.

        Parameters
        ----------
        image : toga.Image
            A toga Image.

        Returns
        -------
        Dict
            The resulting toga numpy array (opencv) Image.
        """
        cv_image = PILImage.open(io.BytesIO(image.data))
        cv_image = asarray(cv_image)
        cv_image = cv.cvtColor(cv_image, cv.COLOR_RGB2BGR)
        return Dict(image=cv_image)


class ToTogaImageProcess(Process):
    def __call__(self, *, image: ndarray, **kwargs) -> Dict:
        """Converts a given numpy array (opencv) to a toga Image.

        Parameters
        ----------
        frame : numpy.ndarray
            The input frame to be converted.

        Returns
        -------
        Dict
            The resulting toga Image.
        """

        toga_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        toga_image = PILImage.fromarray(toga_image)
        toga_image = toga.Image(toga_image)
        return Dict(image=toga_image)
