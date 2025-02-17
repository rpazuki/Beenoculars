
import io

import cv2 as cv
import toga
from numpy import asarray, ndarray
from PIL import Image as PILImage

from beenoculars.image_processing import Process


class ToCVImageProcess(Process):
    def __call__(self, image: toga.Image, /, **kwargs) -> ndarray:
        """Converts a given toga Image to a numpy array (opencv) Image.

        Parameters
        ----------
        image : toga.Image
            A toga Image.

        Returns
        -------
        ndarray
            The resulting toga numpy array (opencv) Image.
        """
        image = PILImage.open(io.BytesIO(image.data))
        image = asarray(image)
        image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
        return image


class ToTogaImageProcess(Process):
    def __call__(self, image: ndarray, /, **kwargs) -> toga.Image:
        """Converts a given numpy array (opencv) to a toga Image.

        Parameters
        ----------
        frame : numpy.ndarray
            The input frame to be converted.

        Returns
        -------
        toga.Image
            The resulting toga Image.
        """

        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image = toga.Image(PILImage.fromarray(image))
        return image
