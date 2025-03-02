import functools
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Mapping

from addict import Dict as DefaultDict
from typing_extensions import Self


class Dict(DefaultDict):
    def __missing__(self, key):
        # raise KeyError(key)
        # calling dict.unassinged properties return None
        return None


# logger
log = logging.getLogger(__name__)


class IncompatibleArgsException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class AbstractPipeline(ABC):
    """An abstract pipeline class.
    """

    def __init__(self, processes=[]):
        self.processes = processes

    def append_command(self, step) -> None:
        self.processes.append(step)

    def __call__(self, /, **kwargs) -> Dict:
        return self.process(**kwargs)

    @abstractmethod
    def process(self, /, **kwargs) -> Dict:
        pass

    @abstractmethod
    def __rshift__(self, other) -> Self:
        pass

    @abstractmethod
    def __mul__(self, other) -> 'ProcessFork':
        pass


class AbstractProcess(ABC):

    @abstractmethod
    def __call__(self, **kwargs) -> Dict:
        """The operation of the process must happen here.

        It can define any number of arguments it like and
        must have one '**kwargs' at the end.

        The returns will be named payload as a Dict object
        and will be passed to the down-stream process or
        return to the caller.
        """
        pass

    def __rshift__(self, other) -> AbstractPipeline:
        """Appends the process to the end of an Process or ImageProcessingPipeline.

           This is an imumutable operation and new ImageProcessingPipeline will be
           returned.

           Example:
                proc1 >> proc2 >> proc3

        Parameters
        ----------
        other : AbstractProcess | ImageProcessingPipeline
            The process or pipeline that will be appended to the given
            process.
            For ProcessFork in the RHS, the output of the ProcessFork
            will be joined by returning a ProcessJoined object.

        Returns
        -------
        AbstractPipeline
            A new (immutable) pipeline object that contains the current
            process followed by 'other' argument.

        Raises
        ------
        ValueError
            Arises when the RHS is not one of the accptable types.
        """
        if issubclass(type(other), AbstractProcess):
            if isinstance(other, ProcessFork):
                other = ProcessJoined(other)
            return ImageProcessingPipeline([self, other])
        elif issubclass(type(other), AbstractPipeline):
            return ImageProcessingPipeline(
                [self] + other.processes)
        else:
            raise ValueError(
                f"The '{type(other)}' must be a AbstractProcess or ImageProcessingPipeline.")

    def __mul__(self, other):
        """Fork two or more processes.

           This is an imumutable operation and new ProcessFork will be
           returned.

           Example:
               p1 * p2 : Forks two processes
               p1 * p2 * p3 : Forks three processes

        Parameters
        ----------
        other : int, ProcessFork, AbstractProcess, ImageProcessingPipeline
            When the RHS is n (int), it is forked to n replicate.
            When the RHS is ProcessFork, AbstractProcess or ImageProcessingPipeline,
            the LHS process stack on its process.

        Returns
        -------
        ProcessFork
            A callable object that forks the processes.

        Raises
        ------
        ValueError
            Raises when the 'other' argument is not an int, a ProcessFork, sub class of
            AbstractProcess, or ImageProcessingPipeline.
            Also, in case for RHS int and LHS ProcessFork, it will raise the error.
        """
        if isinstance(other, int):
            if isinstance(self, ProcessFork):
                raise ValueError(
                    "The 'ProcessFork' has already forked (cannot be multiplied).")
            else:
                return ProcessFork([self] * other)
        if isinstance(other, ProcessFork):
            if isinstance(self, ProcessFork):
                return ProcessFork(self.processes + other.processes)
            else:
                return ProcessFork([self] + other.processes)
        if issubclass(type(other), AbstractProcess):
            return ProcessFork([self, other])
        if issubclass(type(other), ImageProcessingPipeline):
            return ProcessFork([self, other])
        else:
            raise ValueError(
                f"The '{type(other)}' must be an int, a AbstractProcess, ImageProcessingPipeline "
                f"or tuples of both.")


class Process(AbstractProcess):
    """A singleton object for instantiable processes.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Process, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance


class ProcessPassThrough(Process):
    def __call__(self, **kwargs) -> Dict:
        """Payload is simplely pass to the next process."""
        return Dict(**kwargs)


class ProcessJoined(AbstractProcess):
    def __init__(self,
                 forkedProcess: AbstractProcess,
                 kwargs_mapping: Mapping[int, list[tuple[str, str]]] = {}):
        """Join all the forked processes and returns as a single Mapping.

        Parameters
        ----------
        forkedProcess : Process
            The process that has been forked.
        kwargs_mapping : Mapping[int, list[tuple[str, str]]], optional
            Provides the renaming of the processes outputs, by default None.
            The key is the index of the process in the forked process.
            The value is a list of tuples of the old key and the new key.
        """
        self.forkedProcess = forkedProcess
        self.kwargs_mapping = kwargs_mapping

    def __call__(self, **kwargs) -> Dict:
        # First, calls all the sub-processes in the fork.
        tuple_return = self.forkedProcess(**kwargs)
        # Next, if there is any renaming requested in the
        # payloads of the forked sub-processes, we do it here
        for index, names in self.kwargs_mapping.items():
            ret = tuple_return[index]
            for old_key, new_key in names:
                ret[new_key] = ret.pop(old_key)
        # Finally, make a union of all the retuned payloads.
        # Note: the names from returns of higher rank  has precedence
        new_kwargs = tuple_return[0]
        for d in tuple_return[1:]:
            new_kwargs |= d
        return new_kwargs


class ProcessFork(AbstractProcess):
    def __init__(self,
                 processes: list):
        assert len(processes) > 1, "The processes must be more than one."
        self.processes = processes

    def __getitem__(self, key: int) -> AbstractProcess | AbstractPipeline:
        return self.processes[key]

    def __setitem__(self, key: int, process) -> None:
        self.processes[key] = process

    def __call__(self,  **kwargs) -> tuple[Dict, ...]:
        """It calles each sub-processes of the fork and returns thier payload as a tuple."""
        return tuple(p(**kwargs) for p in self.processes)

    def __rshift__(self, other) -> ProcessJoined:
        # It first join the forked instance, and next,
        # calls the abstractProcess rshift to append the
        # RHS to the joined process.
        return ProcessJoined(self) >> other

    def __itruediv__(self, other) -> ProcessJoined:
        return self.__truediv__(other)

    def __truediv__(self, other: Mapping[int, list[tuple[str, str]]]) -> ProcessJoined:
        """combine the output of a forked process.

            Examples:
            forked_process /= {0:[ ('old_name1', 'new_name1'),
                                   ('old_name2', 'new_name2')],
                               1:[ ('old_name3', 'new_name3'),
                                   ('old_name4', 'new_name4')]
                                   }

        Parameters
        ----------
        other : Mapping[int, list[tuple[str, str]]]
            A mapping of .

        Returns
        -------
        ProcessJoined
            A joined processes.

        Raises
        ------
        ValueError
            raises when the 'other' argument is not a type of a mapping.
        """
        if isinstance(other, Mapping):
            assert len(other) <= len(self.processes), "The number of renaming"
            " must be less than or equal to the number of processes."
            return ProcessJoined(self, kwargs_mapping=other)
        else:
            raise ValueError(
                f"The {type(other) =} must be a Mapping[str, int] ")


class ImageProcessingPipeline(AbstractPipeline):
    def __init__(self, processes=[]):
        super(ImageProcessingPipeline, self).__init__(processes)

    def __rshift__(self, other) -> AbstractPipeline:
        """Appends the process to the end of an Process or ImageProcessingPipeline.

           This is an imumutable operation and new ImageProcessingPipeline will be
           returned.

           Example:
                proc1 >> proc2 >> proc3

        Parameters
        ----------
        other : AbstractProcess | ImageProcessingPipeline
            The process or pipeline that will be appended to the given
            pipeline.
            For ProcessFork in the RHS, the output of the ProcessFork
            will be joined by returning a ProcessJoined object inside a
            pipeline.

        Returns
        -------
        AbstractPipeline
            A new (immutable) pipeline object that contains the current
            pipeline followed by 'other' argument.

        Raises
        ------
        ValueError
            Arises when the RHS is not one of the accptable types.
        """
        if issubclass(type(other), AbstractProcess):
            if isinstance(other, ProcessFork):
                other = ProcessJoined(other)
            return ImageProcessingPipeline(self.processes + [other])
        elif isinstance(other, ImageProcessingPipeline):
            return ImageProcessingPipeline(self.processes + other.processes)
        else:
            raise ValueError(
                f"The '{type(other)}' must be a Process or ImageProcessingPipeline.")

    def __mul__(self, other) -> ProcessFork:
        """Fork two or more pipslines.

           This is an imumutable operation and new ProcessFork will be
           returned.

           Example:
               p1 * p2 : Forks two processes/pipelines
               p1 * p2 * p3 : Forks three processes/piplines

        Parameters
        ----------
        other : int, ProcessFork, AbstractProcess, ImageProcessingPipeline
            When the RHS is n (int), it is forked to n replicate.
            When the RHS is ProcessFork, AbstractProcess or ImageProcessingPipeline,
            the LHS process stack on its process.

        Returns
        -------
        ProcessFork
            A callable object that forks the processes.

        Raises
        ------
        ValueError
            Raises when the 'other' argument is not an int, a ProcessFork, sub class of
            AbstractProcess, or ImageProcessingPipeline.
            Also, in case for RHS int and LHS ProcessFork, it will raise the error.
        """
        if isinstance(other, int):
            return ProcessFork([self] * other)
        if isinstance(other, ProcessFork):
            raise ValueError(
                f"The {type(other) =} cannot be mutiplied from LHS of a ImageProcessingPipeline."
            )
        if issubclass(type(other), AbstractProcess):
            return ProcessFork([self, other])
        if issubclass(type(other), ImageProcessingPipeline):
            return ProcessFork([self, other])
        else:
            raise ValueError(
                f"The {type(other) =} must be an int, a Process, ImageProcessingPipeline "
                f"or tuples of both.")

    def process(self, /, **kwargs) -> Dict:
        """Proccess and return the pipeline.

        all kwargs are default values for any processes in down-stream. However,
        the process returned parameters have precedence.

        Returns
        -------
        Dict
            A dict object that conains the processed image and other parameters.

        Raises
        ------
        IncompatibleArgsException
        """
        try:
            payload_kwargs = Dict(**kwargs)
            for index, process in enumerate(self.processes):
                ret: Dict = process(**payload_kwargs)
                # Unino the returned payload with previous ones.
                # This will be passed to next process or return to the caller.
                #
                #  1- Process parameters have precedence over the kwargs.
                #  2- The latest process parameters have precedence over the formeres.
                payload_kwargs |= ret
        except TypeError as e:
            # The name of the class
            def name(obj) -> str: return type(obj).__name__
            if (len(e.args) > 0 and
                    ("missing 1 required keyword-only argument" in e.args[0] or
                     "missing 1 required positional argument" in e.args[0]
                     )):
                if index > 0:
                    previous_process = name(self.processes[index - 1])
                else:
                    previous_process = "(input of the pipline)"
                raise IncompatibleArgsException(
                    f"The process '{name(process)}' received incompatible payload from "
                    f"the previous process '{previous_process}'.")
            else:
                raise e
        return payload_kwargs


class ProcessLogic(AbstractProcess):
    def __init__(self, logic_callback: Callable[..., Dict]):
        self.logic_callback = logic_callback

    def __call__(self, **kwargs) -> Dict:
        return self.logic_callback(**kwargs)


def processLogic(func: Callable[..., Dict]) -> Callable[..., ProcessLogic]:
    """A decorator for creating inline process.

       It can turn a function to a process, as long as the function
       arguments include '**kwargs' and returns a Dict as it payloads.
       In short, decorating a function can turn it into an inline definition
       of a process, which can be joined (>>) or forked (*) by other processes.

       Example:
           @processLogic
           def proc2(condition:bool, **kwargs) -> Dict:
               if condition:
                   return Dict(value=True)
               else:
                   return Dict(value=False)

            proc1 >> proc2()

    Parameters
    ----------
    func : Callable[..., Dict]
        Callable function that contains the logic of creating the process.
        The Callable function must include '**kwargs' in its arguments and
        returns a Dict as it payloads.

    Returns
    -------
    Callable[..., ProcessLogic]
        The decorated process. By calling it without any argument,
        it returns a process that can be joined or forked to others.
    """
    p_logic = ProcessLogic(func)

    def logic() -> ProcessLogic:
        return p_logic
    return logic


class ProcessLogicProperty(AbstractProcess):
    def __init__(self, logic_callback: Callable[..., Dict]):
        self.logic_callback = logic_callback
        self.caller_class = None

    def __call__(self, **kwargs) -> Dict:
        return self.logic_callback(self.caller_class, **kwargs)


def processLogicProperty(func: Callable[..., Dict]) -> property:
    """A decorator for creating inline process inside classes as a property.

       It can turn a class method to a process as a property, as long as the method
       arguments includes '**kwargs' and returns a Dict as it payloads.
       In short, decorating a class method turns it into an inline definition
       of a process, which can be joined (>>) or forked (*) by other processes.

       Example:
           class ClassExample:
               @processLogicProperty
               def proc2(self, condition:bool, **kwargs) -> Dict:
                   if condition:
                       return Dict(value=True)
                   else:
                       return Dict(value=False)
                def another _function(self):
                    pipline = proc1 >> self.proc2

    Parameters
    ----------
    func : Callable[..., Dict]
        A method that defined in a class that contains the logic of creating
        the process. The Callable method must have '**kwargs' in its arguments
        (including the default 'self' argument) and returns a Dict as it payloads.

    Returns
    -------
    Callable[..., ProcessLogic]
        The decorated process. By using it like a property,
        it returns a process that can be joined or forked to others.
    """
    p_logic = ProcessLogicProperty(func)

    def logic(caller) -> ProcessLogicProperty:
        p_logic.caller_class = caller
        return p_logic
    # Turns the return to a property with a getter method
    logic_property = property(fget=logic)
    return logic_property


class ProcessFactory:
    def __init__(self, factory_callback: Callable[..., AbstractProcess]):
        self.factory_callback = factory_callback

    def __call__(self, *args: Any, **kwargs) -> AbstractProcess:
        return self.create(*args, **kwargs)

    def create(self, *args: Any, **kwargs) -> AbstractProcess:
        """Create a parametrised process (arguments) to be attached and called later."""
        process = self.factory_callback(*args, **kwargs)
        return process


def processFactory(cache: bool,
                   cache_size: int = 256):
    """A factory decorator that turns a function to a process.

       The function must return a process or ImageProcessingPipeline.

    Parameters
    ----------
    cache : bool
        Cache the created pipeline based on the arguments that pass to
        the factory function.
    cache_size : int, optional
        The size of the cache, by default 256
    """
    def decorator(func):
        p_factory = ProcessFactory(func)

        if cache:
            @functools.lru_cache(cache_size)
            def cached_factory(*args, **kwargs) -> AbstractProcess:
                """Parametrisation arguments are passed here."""
                return p_factory.create(*args, **kwargs)
            return cached_factory
        else:
            def factory(*args, **kwargs) -> AbstractProcess:
                """Parametrisation arguments are passed here."""
                return p_factory.create(*args, **kwargs)
            return factory
    return decorator
