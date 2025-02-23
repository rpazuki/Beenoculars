#  import copy
import logging
from abc import abstractmethod
from multiprocessing.context import ForkProcess
from typing import Any, Callable, Mapping

#  from numpy import ndarray

# logger
log = logging.getLogger(__name__)


def processLogic(func):
    def logic(*args, **kwargs):
        """Processes arguments are passed here."""
        return ProcessLogic(func)(*args, **kwargs)
    return logic


class AbstractProcess(object):
    @abstractmethod
    def __call__(self, *args: Any) -> Any:
        pass

    def __iadd__(self, other):
        return self.__add__(other)

    def __add__(self, other):
        if issubclass(type(other), AbstractProcess):
            return ImageProcessingPipeline([self, other])
        elif issubclass(type(other), ImageProcessingPipeline):
            return ImageProcessingPipeline([self] + other.processes)
        else:
            raise ValueError(
                f"The '{type(other)}' must be a Process.")

    def __mul__(self, other):
        """Fork two or more processes.

        / -p1
        - -p2
        | -p3

        e.g.
        p1 * p2 : Forks two processes
        p1 * p2 * p3 : Forks three processes

        Parameters
        ----------
        other : AbstractProcess, ImageProcessingPipeline,
                tuple(AbstractProcess, ImageProcessingPipeline)
            The process to fork with.

        Returns
        -------
        ProcessFork
            A callable object that forks the processes.

        Raises
        ------
        ValueError
            The 'other' argument must be a Process, ImageProcessingPipeline or
            tuples of both.
        """
        if isinstance(other, int):
            if isinstance(self, ForkProcess):
                raise ValueError(
                    "The 'ForkProcess' has already forked (cannot be multiplied).")
            else:
                return ProcessFork([self] * other)
        if isinstance(other, ForkProcess):
            if isinstance(self, ForkProcess):
                return ProcessFork(self.processes + other.processes)
            else:
                return ProcessFork([self] + other.processes)
        if issubclass(type(other), AbstractProcess):
            return ProcessFork([self, other])
        if issubclass(type(other), ImageProcessingPipeline):
            return ProcessFork([self, other])
        else:
            raise ValueError(
                f"The '{type(other)}' must be an int, a Process, ImageProcessingPipeline "
                f"or tuples of both.")

    # def __truediv__(self, other):
    #     """IF two or more processes.

    #     / -p1 \
    #     - -p2 -  returns ret1 or ret2

    #     e.g.
    #     p1 / p2 : IF two processes

    #     Parameters
    #     ----------
    #     other : AbstractProcess, ImageProcessingPipeline
    #         The process to select from based on if condition.

    #     Returns
    #     -------
    #     ProcessIf
    #         A callable object that select the processes base on if condition.

    #     Raises
    #     ------
    #     ValueError
    #         The 'other' argument must be a Process or ImageProcessingPipeline
    #         or tuples of both
    #     """
    #     if issubclass(type(other), AbstractProcess):
    #         return ProcessIf(self, other)
    #     if issubclass(type(other), ImageProcessingPipeline):
    #         return ProcessIf(self, other)
    #     if (isinstance(other, tuple) and
    #         all(issubclass(type(p), AbstractProcess) |
    #             issubclass(type(p), ImageProcessingPipeline) for p in other)):
    #         return ProcessIfElse([self] + list(other))
    #     else:
    #         raise ValueError(
    #             f"The '{type(other)}' must be a Process, ImageProcessingPipeline "
    #             f"or tuples of both.")

    # def __matmul__(self, other):
    #     if isinstance(other, Mapping):
    #         return ProcessCurrying(self, other)
    #     else:
    #         raise ValueError(
    #             f"The '{type(other)}' must be a Mapping.")


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


class ProcessLogic(AbstractProcess):
    def __init__(self, logic_callback: Callable[..., AbstractProcess]):
        self.logic_callback = logic_callback

    def __call__(self, *args: Any, **kwargs) -> Any:
        """Parametrisation arguments are passed to the logic_callback function."""
        process = self.logic_callback(*args, **kwargs)
        return process


class ProcessJoined(AbstractProcess):
    def __init__(self,
                 forkedProcess: Process,
                 kwargs_mapping: Mapping[str, int]):
        self.forkedProcess = forkedProcess
        # if "image" not in kwargs_mapping:
        #     raise ValueError("The 'image' key must be in the kwargs_mapping.")
        self.kwargs_mapping = kwargs_mapping

    def __call__(self, *args: Any, **kwargs) -> Any:
        tuple_return = self.forkedProcess(*args, **kwargs)
        # image_index = self.kwargs_mapping["image"]
        # image = tuple_return[image_index]
        # other_kvargs = {k: tuple_return[index]
        #                 for k, index in self.kwargs_mapping.items() if k != "image"}
        # return image, other_kvargs
        new_kwargs = {k: tuple_return[index]
                      for k, index in self.kwargs_mapping.items()}
        return new_kwargs


class ProcessFork(AbstractProcess):
    def __init__(self,
                 processes: list[Process]):
        assert len(processes) > 1, "The processes must be more than one."
        self.processes = processes

    def __getitem__(self, key: int) -> Process:
        return self.processes[key]

    def __call__(self, *args: Any, **kwargs) -> list:
        return tuple(p(*args, **kwargs)
                     for p in self.forkedProcess.processes)
        # raise NotImplementedError(
        #     "The forked processes must not be called directly. "
        #     "Use '/=' operator to join the outputs."
        # )

    def __itruediv__(self, other):
        """combine the output of a forked process.

        / -p1 \
        - -p2 -  returns ret1 or ret2

        e.g.
        p1 /= {"image": 1, "backgound":0} : use the output as the kwargs

        Parameters
        ----------
        other : AbstractProcess, ImageProcessingPipeline
            The process to select from based on if condition.

        Returns
        -------
        ProcessIf
            A callable object that select the processes base on if condition.

        Raises
        ------
        ValueError
            The 'other' argument must be a Process or ImageProcessingPipeline
            or tuples of both
        """
        if isinstance(other, Mapping):
            return ProcessJoined(self, other)
        else:
            raise ValueError(
                f"The '{type(other)}' must be a Mapping[str, int] ")


# class ProcessIf(AbstractProcess):
#     def __init__(self, process1: Process, process2: Process):
#         self.process1 = process1
#         self.process2 = process2

#     def __call__(self, ifCondition, *args: Any, **kwargs) -> Any:
#         condition = ifCondition() if callable(ifCondition) else ifCondition
#         if condition:
#             return self.process1(*args, **kwargs)
#         else:
#             return self.process2(*args, **kwargs)


# class ProcessIfElse(AbstractProcess):
#     def __init__(self, processes: list[Process]):
#         assert len(processes) > 1, "The processes must be more than one."
#         self.processes = processes

#     def __call__(self, matchCondition, *args: Any, **kwargs) -> Any:
#         condition_number = matchCondition() if callable(
#             matchCondition) else matchCondition
#         assert condition_number < len(
#             self.processes), "condition number must be less than number of processes."
#         return self.processes[condition_number](*args, **kwargs)


# class ProcessCurrying(AbstractProcess):
#     def __init__(self, process: Process, kwargs):
#         self.process = process
#         self.kwargs = kwargs

#     def __call__(self, *args: Any, **kwargs) -> Any:
#         new_kwargs = copy.copy(self.kwargs)
#         for k, v in new_kwargs.items():
#             if callable(v):
#                 new_kwargs[k] = v()
#         # Currying parameters have precedence
#         for k, v in kwargs.items():
#             if k not in new_kwargs:
#                 new_kwargs[k] = v
#         # Caller parameters have precedence
#         # for k, v in kwargs.items():
#         #     new_kwargs[k] = v

#         return self.process(*args, **new_kwargs)


class ImageProcessingPipeline:
    def __init__(self, processes=[]):
        self.processes = processes

    def append_command(self, step):
        self.processes.append(step)

    def __iadd__(self, other):
        return self.__add__(other)

    def __add__(self, other):
        if issubclass(type(other), AbstractProcess):
            return ImageProcessingPipeline(self.processes + [other])
        elif isinstance(other, ImageProcessingPipeline):
            return ImageProcessingPipeline(self.processes + other.processes)
        else:
            raise ValueError(
                f"The '{type(other)}' must be a Process or ImageProcessingPipeline.")

    def __mul__(self, other):
        if isinstance(other, int):
            return ProcessFork([self] * other)
        if isinstance(other, ForkProcess):
            raise ValueError(
                f"The '{type(other)}' cannot be mutiplied from LHS of a ImageProcessingPipeline."
            )
        if issubclass(type(other), AbstractProcess):
            return ProcessFork([self, other])
        if issubclass(type(other), ImageProcessingPipeline):
            return ProcessFork([self, other])
        else:
            raise ValueError(
                f"The '{type(other)}' must be an int, a Process, ImageProcessingPipeline "
                f"or tuples of both.")

    # def __truediv__(self, other):
    #     if issubclass(type(other), AbstractProcess):
    #         return ProcessIf(self, other)
    #     if issubclass(type(other), ImageProcessingPipeline):
    #         return ProcessIf(self, other)
    #     if (isinstance(other, tuple) and
    #         all(issubclass(type(p), AbstractProcess) |
    #             issubclass(type(p), ImageProcessingPipeline) for p in other)):
    #         return ProcessIfElse([self] + list(other))
    #     else:
    #         raise ValueError(
    #             f"The '{type(other)}' must be a Process, ImageProcessingPipeline "
    #             f"or tuples of both.")

    # def __call__(self, image, **kwargs):

    def __call__(self, image, **kwargs):
        return self.process(image, **kwargs)

    # def process(self, image, **kwargs):
    def process(self, image, **kwargs):
        for process in self.processes:
            ret = process(image, **kwargs)
            if isinstance(ret, Mapping):
                if "image" not in ret:
                    raise ValueError("The 'image' key must be in the return.")
                for k, v in reversed(ret.items()):
                    if k != "image":
                        kwargs[k] = v
                image = ret["image"]
            else:
                image = ret
            # ret = process(image, **kwargs)
            # if isinstance(ret, ndarray):
            #     image = ret
            # elif isinstance(ret, tuple) and len(ret) == 2:
            #     image = ret[0]
            #     other_ret = ret[1]
            #     for k, v in other_ret.items():
            #         kwargs[k] = v
            # else:
            #     image = ret
            #     # raise TypeError(
            #     #     "The reruned value is not Any or a (Any, Any) type.")

        return ret
