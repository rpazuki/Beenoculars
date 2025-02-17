from abc import abstractmethod

import beenoculars.core as core
import beenoculars.image_processing as imp


class SyncImageService(core.SyncServiceStrategy):
    def __init__(self) -> None:
        registry = imp.ProcessesRegistry()
        self.toOpenCV = registry[imp.ToOpenCVImageProcess]
        self.toFramework = registry[imp.ToFrameworkImageProcess]

    @abstractmethod
    def _get_original_image(self, app):
        pass

    @abstractmethod
    def _set_image(self, app, image):
        pass


class AsyncImageService(core.AsyncServiceStrategy):
    def __init__(self) -> None:
        registry = imp.ProcessesRegistry()
        self.toOpenCV = registry[imp.ToOpenCVImageProcess]
        self.toFramework = registry[imp.ToFrameworkImageProcess]

    @abstractmethod
    def _get_original_image(self, app):
        pass

    @abstractmethod
    def _set_image(self, app, image):
        pass
