from __future__ import annotations

import ast
import inspect
from abc import abstractmethod
from typing import TypeVar

from beenoculars.core.__core__ import AbstractApp, AbstractLayout, Configurable

Box = TypeVar("Box")


class Layout[Box](AbstractLayout):

    def __init__(self, app: MultiLayoutApp[Box]) -> None:
        super().__init__(app)
        self._app = app

    @property
    def ml_app(self) -> MultiLayoutApp[Box]:
        return self._app

    @property
    def main_box(self) -> Box:
        if self._box is None:
            raise ValueError("box has not been initialized (_build_box).")
        return self._box

    def build_layout(self) -> Box:
        """Build the main window of the app and its layout.
        """
        #
        self._box = self._build_box()
        #
        return self._box

    @abstractmethod
    def _build_box(self) -> Box:
        """Build the layout box and all the required UI elements.

           Also, all the buttons that has an id registred in ServiceRegistry
           will be bind to on_press handlers.

        Parameters
        ----------
        image_view : toga.ImageView
            Every app have and ImageView that the layout class must
            include it in a box.
        """
        pass


class Component[Box, *Ts](Configurable):
    def __init__(self, layout: StackedLayout[Box, *Ts], **kwargs) -> None:
        self._layout = layout
        super(Component, self).__init__(**kwargs)

    @property
    def ml_app(self) -> MultiLayoutApp[Box]:
        return self._layout.ml_app

    @property
    def parent_layout(self) -> StackedLayout[Box, *Ts]:
        return self._layout

    def on_load(self):
        pass

    def on_end(self):
        pass


T = TypeVar("T", bound=Component)
Ts = TypeVar("Ts", bound=Component)


def _get_component_passthrough(cls):
    target = cls
    component_methods = []

    def visit_FunctionDef(node):
        for n in node.decorator_list:
            name = ''
            if isinstance(n, ast.Call):
                name = n.func.attr if isinstance(
                    n.func, ast.Attribute) else n.func.id  # type: ignore
            else:
                name = n.attr if isinstance(n, ast.Attribute) else n.id
            if name == 'component_method':
                component_methods.append(node.name)

    node_iter = ast.NodeVisitor()
    node_iter.visit_FunctionDef = visit_FunctionDef
    node_iter.visit(ast.parse(inspect.getsource(target)))

    return component_methods


class StackedLayout[Box, *Ts](Layout[Box]):

    def __init__(self,
                 app: MultiLayoutApp[Box],
                 box: Box,
                 *types: *type[Ts]):  # type: ignore
        assert len(types) > 0, "At least one KivyComponent type is needed."
        self._box = box
        self.types = types
        self._instances = {}
        super(StackedLayout, self).__init__(app)

    def __getitem__(self, key: type[T]) -> T:
        return self.instances[key.__name__]

    def _init_component(self, component_type: type[T]) -> T:
        """override this method if there are component specific initilisations.

        Parameters
        ----------
        component_type : type[T]
            Component's type

        Returns
        -------
        T
            An instance of the component.
        """
        return component_type(layout=self)

    @property
    def instances(self) -> dict:
        if self._instances == {}:
            def name(component_type) -> str: return component_type.__name__
            self._instances = {
                name(component_type): self._init_component(component_type)
                for component_type in self.types
            }

        return self._instances

    @property
    def _name(self) -> str:
        return ":".join(t.__qualname__ for t in self.types)

    def build_layout(self) -> Box:
        #
        self._build_box()
        #
        return self._box

    @abstractmethod
    def _add_to_main_box(self, box: Box, element: Box):
        pass

    def _build_box(self):
        """Construct and show the content layout of Toga application."""
        #
        for instance, component_type in zip(self.instances.values(), self.types):
            self._add_to_main_box(self._box, instance)
            # passthrough the methods of the components to the layout
            # find the components methods that has @component_method decorator
            methods = _get_component_passthrough(component_type)
            for name in methods:
                # define the same method for the layout
                m = getattr(instance, name)
                setattr(self, name, m)
            #
            instance.on_load()
        return self._box

    def _set_config(self):
        """Layout related config (e.g. bindings).
        """
        #
        super()._set_config()
        for instance in self.instances.values():
            instance._set_config()

    def on_end(self):
        for component in self.instances.values():
            component.on_end()


class MultiLayoutApp[Box](AbstractApp):

    def __init__(self,
                 main_container: Box,
                 init_layout: Layout[Box],
                 **kwargs) -> None:
        if not isinstance(init_layout, Layout):
            raise ValueError(
                f"The {init_layout=} argument must be a subclass of 'TogaLayout'.")
        #
        self._main_container = main_container
        self._layout_lookup = {init_layout._name: init_layout}
        self._current_layout = init_layout
        #
        super(MultiLayoutApp, self).__init__(
            init_layout, **kwargs)

    @property
    def main_container(self) -> Box:
        return self._main_container

    @property
    def current_layout(self) -> Layout[Box]:
        return self._current_layout

    @abstractmethod
    def _add_layout(self, layout: Layout[Box]):
        pass

    def show_layout(self, layout: Layout[Box]):
        if layout._name not in self._layout_lookup:
            self._layout_lookup[layout._name] = layout
            self.layout = layout
            #
            # Call on_load in AbstractApp to register the event and
            # build to layout. It must be called once
            # Layout's on_load() will be called inside this function
            self.on_load()
            #
            self._add_layout(self.layout)
        else:
            layout = self._layout_lookup[layout._name]
            #
            self._add_layout(layout)
            #
            self.layout = layout
            # Call layout's on_load for any reloading logic
            self.layout.on_load()
            #

    def on_end(self) -> bool:
        for layout in self._layout_lookup.values():
            layout.on_end()
        return super().on_end()
