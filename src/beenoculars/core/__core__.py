import logging
from abc import ABC, abstractmethod
from enum import Enum
from inspect import signature
from typing import Any, Mapping

log = logging.getLogger(__name__)


class UIFramework(Enum):
    TOGA = 0
    KIVY = 1


class EventType(Enum):
    ON_PRESS = 0
    ON_RELEASE = 1
    ON_CHANGE = 2
    ON_TOUCH_DOWN = 3
    ON_TOUCH_MOVE = 4
    ON_TOUCH_UP = 5
    BIND = 100

    def get_all_eventTypes():
        return vars(EventType)['_member_names_']


class ServiceStrategy(ABC):
    """An abstract class for handeling UI event callbacks
    """

    @abstractmethod
    def handle_event(self, widget: Any, app, *args, **kwargs):
        """An abstract class for handeling UI sync event callbacks
        """
        pass

    def on_exit(self):
        """The event handler that will be invoked when the app is about to exit.
        """
        pass


class Event:
    def __init__(self,
                 id: str,
                 eventType: EventType,
                 service: ServiceStrategy,
                 property_name: str = None,
                 extra_kwargs: Mapping = None
                 ) -> None:
        self.id = id
        self.eventType = eventType
        self.service = service
        self.property_name = property_name
        self.extra_kwargs = extra_kwargs

    def element_event(self, element):
        return getattr(element, self.eventType.name.lower())


class AbstractLayout(ABC):
    def __init__(self) -> None:
        super(AbstractLayout, self).__init__()

    @abstractmethod
    def build_layout(self) -> Any:
        pass


class AbstractApp(ABC):
    def __init__(self,
                 layout: AbstractLayout,
                 **kwargs) -> None:
        super(AbstractApp, self).__init__(**kwargs)
        self.layout = layout
        self._event_dispatchers_table = {}
        for t in EventType.get_all_eventTypes():
            self._event_dispatchers_table[t] = {}

    @property
    def event_dispatchers_table(self):
        """Stores different event_dispatchers per EventType.

        event_dispatchers_table is dictionary or dictionaries that
        EventType is its key and event_dispatchers are dictionaries
        of (id : UI element).
        """
        return self._event_dispatchers_table

    def on_begin(self):
        """The event handler that will be invoked when the app is about to start.

        It calls the build_layout of Layout instance, stores all UI elements with
        id and suport of one or more events in event_dispatchers_table, and registers
        them in ServiceRegistry.
        """
        root = self.layout.build_layout()
        self.__enumerate_elements(root)
        # Event bindings to dispatcher happens here
        registry = ServiceRegistry()
        for id, event in registry.events.items():
            event_dispatcher = self.event_dispatchers_table[event.eventType.name]
            if id not in event_dispatcher:
                raise ValueError(
                    f" Widget id:'{id}' for the {event.eventType.name} handler "
                    f"has no corresponding UI. Check the bindings map.")
            element = event_dispatcher[id]
            registry.register_service(event,
                                      element,
                                      app=self)

    def on_end(self):
        """The event handler that will be invoked when the app is about to exit.

        It calls the on_exit of all services in the ServiceRegistry.
        """
        registry = ServiceRegistry()
        registry.on_exit()
        return True

    def __enumerate_elements(self, root):
        """Recursivly searches and records all elements.
        """

        def creat_method_checker(name):
            """Create a function that checks availibility of a method
            """
            def checker(obj):
                """A combinations of attribute name and callable"""
                method = getattr(obj, name, None)
                return method is not None and callable(method)

            return checker

        event_checkers = [(t, creat_method_checker(t.lower()))
                          for t in EventType.get_all_eventTypes()]

        def recursive(parent):
            """Recusricly check all UI's tree elements.

               If the element has both an id and a corresponding
               event, it will be stored in event_dispatchers.
            """
            for child in parent.children:
                # event_checkers contains both the eventType and corresponding
                # method (has_event) that check the availibity of the event.
                # e.g. for EventType.ON_PRESS, has_event looks for UI element's
                # on_press event support.
                for eventType, has_event in event_checkers:
                    if has_event(child) and hasattr(child, "id") is True:
                        # event_dispatchers_table is dictionary or dictionaries
                        event_dispatchers = self.event_dispatchers_table[eventType]
                        event_dispatchers[child.id] = child
                recursive(child)

        recursive(root)


class ServiceRegistry(object):
    """A singleton object that store the required (id: ServiceStrategy).
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceRegistry, cls).__new__(cls)
            # Put any initialization here.
            cls._instance._dispatcher = EventDispatcher()
        return cls._instance

    __events = {}
    _ui_framework = UIFramework.TOGA

    @property
    def ui_framework(self) -> UIFramework:
        return self._instance._ui_framework

    @ui_framework.setter
    def ui_framework(self, value: UIFramework):
        self._instance._ui_framework = value

    @property
    def dispatcher(self):
        return self._instance._dispatcher

    @property
    def events(self):
        return self._instance.__events

    def bind_event(self, event: Event):
        self.events[event.id] = event

    def get_event_info(self, id) -> Event:
        return self.events.get(id, None)

    def register_service(self, event: Event, element: Any, app: AbstractApp):
        """Register a ServiceStrategy for the given event, UI element and app.

           A callback will be attached to the event handler of the UI element.
           If the UI element has also a handler, it will be included in the call
           qeue.


        Parameters
        ----------
        event : Event
            The event object that includes id and ServiceStrategy.
        element : Any
            UI element that can handel th event.
        app : AbstractApp
            The app object.
        """
        if event.extra_kwargs is not None and not isinstance(event.extra_kwargs, Mapping):
            raise ValueError(
                f" Widget id:'{event.id}' ({type(element).__name__}) "
                f"asked for {event.eventType.name} handler, but did not provide "
                f"the binding arguments (Mapping). Check the bindings map.")
        #

        def attach(callback):
            # setattr(element, registeredEventType.name.lower(), callback)
            match self.ui_framework:
                case UIFramework.TOGA:
                    from toga.handlers import wrapped_handler
                    handler = wrapped_handler(element, callback)
                    # e.g. element.on_press = handler
                    setattr(element, event.eventType.name.lower(), handler)
                case UIFramework.KIVY:
                    # Only BIND
                    if event.eventType == EventType.BIND:
                        if event.property_name == "":
                            raise ValueError(
                                f" Widget id:'{event.id}' ({type(element).__name__}) "
                                f"asked for {event.eventType.name} handler, but did not "
                                f"provide the 'property_name'. Check the bindings map.")
                        if not isinstance(event.property_name, str):
                            raise ValueError(
                                f" Widget id:'{event.id}' ({type(element).__name__}) "
                                f"asked for {event.eventType.name} handler, but did not provide "
                                f"the binding argument name (str). Check the bindings map.")
                        # e.g. switch.bind(active=callback)
                        kwrgs = {event.property_name: callback}
                        element.bind(**kwrgs)
                    else:
                        # e.g. button.bind(on_press=callback)
                        kwrgs = {event.eventType.name.lower(): callback}
                        element.bind(**kwrgs)
                case _:
                    raise ValueError(
                        f" Unknown UI Framework: {self.ui_framework}")
        #
        element_event = event.element_event(element)
        if hasattr(element_event, "_raw"):
            handler = element_event._raw  # This is toga's wrapped_handler attribute
        else:
            handler = element_event  # kivy

        #
        match event.service:
            case SyncServiceStrategy():
                if handler is not None:
                    self.dispatcher.register_framework(event.id, handler)
                self.dispatcher.register(event.id, event.service.handle_event)
                handler_2 = self.dispatcher.service_callback(event.id,
                                                             element,
                                                             app,
                                                             event.extra_kwargs)
                attach(handler_2)
            case AsyncServiceStrategy():
                if handler is not None:
                    self.dispatcher.register_async_framework(event.id, handler)
                self.dispatcher.register_async(
                    event.id, event.service.handle_event)
                handler_2 = self.dispatcher.service_async_callback(event.id,
                                                                   element,
                                                                   app,
                                                                   event.extra_kwargs)
                attach(handler_2)
            case _:
                log.warning(
                    f" Widget id:'{event.id}' ({type(element).__name__}) "
                    f"did not bind to any {event.eventType.name} handler. Check the bindings map.")

    def on_exit(self):
        """The event handler that will be invoked when the app is about to exit.

        It calls the on_exit of all registred services.
        """
        for eventInfo in self.events.values():
            eventInfo.service.on_exit()


class EventDispatcher:
    """Event dispatcher that binds the UI elements call back to EventStrategy instances.

    This is a lightweight event dispatcher that can support both sync and async calls.
    """

    def __init__(self):
        self.listeners = {}
        self.listeners_framework = {}
        self.async_listeners = {}
        self.async_listeners_framework = {}

    #
    def register(self, event_name: str, handler):
        """Register a synchronous callback for an event.

        Parameters
        ----------
        event_name : str
            The name of the event to register.
        handler : function
            The function to call when the event is triggered.
        """
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(handler)

    def register_framework(self, event_name: str, handler):
        """Register a synchronous callback for an event that has already binded in the framework.

        Parameters
        ----------
        event_name : str
            The name of the event to register.
        handler : function
            The function to call when the event is triggered.
        """
        if event_name not in self.listeners_framework:
            self.listeners_framework[event_name] = []
        self.listeners_framework[event_name].append((handler,
                                                     signature(handler)))

    def register_async(self, event_name: str, async_handler):
        """Register an asynchronous callback for an event.

        Parameters
        ----------
        event_name : str
            The name of the event to register.
        async_handler : function
            The async function to call when the event is triggered.
        """

        if event_name not in self.async_listeners:
            self.async_listeners[event_name] = []
        self.async_listeners[event_name].append(async_handler)

    def register_async_framework(self, event_name: str, async_handler):
        """Register an asynchronous callback for an event that has already binded in the framework.

        Parameters
        ----------
        event_name : str
            The name of the event to register.
        async_handler : function
            The async function to call when the event is triggered.
        """

        if event_name not in self.async_listeners_framework:
            self.async_listeners_framework[event_name] = []
        self.async_listeners_framework[event_name].append((async_handler,
                                                           signature(async_handler)))
    #

    def dispatch(self,
                 event_name: str,
                 widget: Any,
                 app: AbstractApp,
                 extrakwargs: Mapping,
                 *args,
                 **kwargs):
        """Dispatch a synchronous event to all registered callbacks.

        Parameters
        ----------
        event_name : str
            The name of the event to dispatch.
        widget : Any
            UI element.
        app : AbstractApp
            The AbstractApp subclass that registred the elements.
        extrakwargs : Mapping
            Extra key-value paires can be provided to pass to the handler.
            If the value is a callable, it is called each time the event happens.
            This is useful when the arguments need to be updated, e.g., from the
            value in the UI.
        """
        if ServiceRegistry().ui_framework == UIFramework.TOGA:
            for callback, sig in self.listeners_framework.get(event_name, []):
                callback(*args, **kwargs)

        for callback in self.listeners.get(event_name, []):
            if extrakwargs is None:
                callback(widget, app, *args, **kwargs)
            else:
                kwargs2 = {}
                for k, v in extrakwargs.items():
                    if callable(v):
                        kwargs2[k] = v()
                    else:
                        kwargs2[k] = v
                callback(widget, app, **kwargs2)

    async def dispatch_async(self,
                             event_name: str,
                             widget: Any,
                             app: AbstractApp,
                             extrakwargs: Mapping,
                             *args,
                             **kwargs):
        """Dispatch a asynchronous event to all registered callbacks.

        Parameters
        ----------
        event_name : str
            The name of the event to dispatch.
        widget : Any
            UI element.
        app : AbstractApp
            The AbstractApp subclass that registred the elements.
        extrakwargs : Mapping
            Extra key-value paires can be provided to pass to the handler.
            If the value is a callable, it is called each time the event happens.
            This is useful when the arguments need to be updated, e.g., from the
            value in the UI.
        """
        if ServiceRegistry().ui_framework == UIFramework.TOGA:
            for callback, sig in self.async_listeners_framework.get(event_name, []):
                callback(*args, **kwargs)

        for callback in self.async_listeners.get(event_name, []):
            if extrakwargs is None:
                await callback(widget, app, *args, **kwargs)
            else:
                kwargs2 = {}
                for k, v in extrakwargs.items():
                    if callable(v):
                        kwargs2[k] = v()
                    else:
                        kwargs2[k] = v
                await callback(widget, app, **kwargs2)

    def service_callback(self, id: str, widget: Any, app: AbstractApp, extrakwargs: Mapping):
        """Create a synchronous widget callback for a ServiceStrategy instance.

        Parameters
        ----------
        id : str
            The ID of the widget.
        widget : Any
            The UI element that registers the and will call the callback.
        app : AbstractApp
            The application instance.
        extrakwargs : Mapping
            Extra argument that maybe provided on binding table.

        Returns
        -------
        function
            A decorated callback function.
        """
        def callback(*args, **kwargs):
            self.dispatch(id, widget, app, extrakwargs, *args, **kwargs)

        return callback

    def service_async_callback(self, id: str, widget: Any, app: AbstractApp, extrakwargs: Mapping):
        """Create an asynchronous widget callback for a ServiceStrategy instance.

        Parameters
        ----------
        id : str
            The ID of the widget.
        widget : Any
            The UI element that registers the and will call the callback.
        app : AbstractApp
            The application instance.
        extrakwargs : Mapping
            Extra argument that maybe provided on binding table.

        Returns
        -------
        function
            A decorated async callback function.
        """
        async def async_callback(*args, **kwargs):
            await self.dispatch_async(id, widget, app, extrakwargs, *args, **kwargs)

        return async_callback


class SyncServiceStrategy(ServiceStrategy):
    """An abstract class for handeling UI sync event callbacks
    """

    @abstractmethod
    def handle_event(self, widget: Any, app: AbstractApp, *args, **kwargs):
        """Sync event handler

        Parameters
        ----------
        widget : Any
            The widget that called the handler.
        app : AbstractApp
            The parent application of the widget.
        """
        return NotImplemented


class AsyncServiceStrategy(ServiceStrategy):
    """An abstract class for handeling UI async event callbacks
    """

    @abstractmethod
    async def handle_event(self, widget: Any, app: AbstractApp, *args, **kwargs):
        """Async event handler.

        Parameters
        ----------
        widget : Any
            The widget that called the handler.
        app : AbstractApp
            The parent application of the widget.
        """
        return NotImplemented
