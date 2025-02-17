import copy
import logging
from abc import abstractmethod
from typing import Any, Mapping

# logger
log = logging.getLogger(__name__)


class AbstractProcess(object):
    @abstractmethod
    def __call__(self, *args: Any) -> Any:
        pass

    def __iadd__(self, other):
        return self.__add__(other)

    def __add__(self, other):
        if isinstance(other, Process):
            return ImageProcessingPipeline([self, other])
        elif isinstance(other, ProcessCurrying):
            return ImageProcessingPipeline([self, other])
        else:
            raise ValueError(
                f"The '{type(other)}' must be a Process.")

    def __matmul__(self, other):
        if isinstance(other, Mapping):
            return ProcessCurrying(self, other)
        else:
            raise ValueError(
                f"The '{type(other)}' must be a Mapping.")


class Process(AbstractProcess):
    """A singleton object for each process.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Process, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    @abstractmethod
    def __call__(self, *args: Any) -> Any:
        pass


class ProcessCurrying(AbstractProcess):
    def __init__(self, process: Process, kwargs):
        self.process = process
        self.kwargs = kwargs

    def __call__(self, *args: Any, **kwargs) -> Any:
        new_kwargs = copy.copy(self.kwargs)
        for k, v in new_kwargs.items():
            if callable(v):
                new_kwargs[k] = v()
        # Currying parameters have precedence
        for k, v in kwargs.items():
            if k not in new_kwargs:
                new_kwargs[k] = v
        # Caller parameters have precedence
        # for k, v in kwargs.items():
        #     new_kwargs[k] = v

        return self.process(*args, **new_kwargs)


class ImageProcessingPipeline:
    def __init__(self, processes=[]):
        self.processes = processes

    def append_command(self, step):
        self.processes.append(step)

    def __iadd__(self, other):
        return self.__add__(other)

    def __add__(self, other):
        if isinstance(other, Process):
            return ImageProcessingPipeline(self.processes + [other])
        if isinstance(other, ProcessCurrying):
            return ImageProcessingPipeline(self.processes + [other])
        elif isinstance(other, ImageProcessingPipeline):
            return ImageProcessingPipeline(self.processes + other.processes)
        else:
            raise ValueError(
                f"The '{type(other)}' must be a Process or ImageProcessingPipeline.")

    def __call__(self, image, **kwargs):
        return self.process(image, **kwargs)

    def process(self, image, **kwargs):
        for process in self.processes:
            image = process(image, **kwargs)
        return image
