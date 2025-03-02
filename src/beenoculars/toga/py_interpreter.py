import logging
from abc import abstractmethod

import toga
from toga.style import Pack
from toga.style.pack import CENTER, COLUMN, ROW  # type: ignore

from beenoculars.core import AbstractApp, AbstractLayout

log = logging.getLogger(__name__)


class InterpreterLayout(AbstractLayout):
    def __init__(self):
        super(InterpreterLayout, self).__init__()
        self._main_box = None

    @property
    def main_box(self) -> toga.Box:
        if self._main_box is None:
            raise ValueError("Main box has not been initialized.")
        return self._main_box

    def build_layout(self) -> toga.Box:
        """Build the main window of the app and its layout.
        """
        self._main_box = toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER, flex=1)
        )
        #
        self._build_layout()
        #
        return self._main_box

    @abstractmethod
    def _build_layout(self):
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


class TwoColumnsLayout(InterpreterLayout):

    def _build_layout(self):
        """Construct and show the content layout of Toga application."""
        log.info("TwoColumnsLayout startup")
        #
        b = toga.Box(style=Pack(
            direction=COLUMN, alignment=CENTER, flex=1))
        b1 = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER))
        b.add(b1)

        def clear(widget):
            self.code_textbox.value = ""
            self.output_textbox.value = ""

        def run(widget):
            import sys
            from io import StringIO
            c = self.code_textbox.value
            try:
                old_stdout = sys.stdout
                sys.stdout = mystdout = StringIO()
                cc = compile(c.replace("‘", "'"), '<string>', 'exec')
                exec(cc)
                sys.stdout = old_stdout
                out = mystdout.getvalue()
                self.output_textbox.value = out
            except Exception as e:
                self.output_textbox.value = f"Error: \n {e}"

            self.output_textbox.scroll_to_bottom()

        btn_run = toga.Button("Run", style=Pack(padding=4),
                              on_press=run)
        btn_clear = toga.Button("Clear", style=Pack(padding=4),
                                on_press=clear)
        b1.add(btn_run)
        b1.add(btn_clear)
        #
        b2 = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, flex=1))
        b.add(b2)
        c1 = toga.Box(style=Pack(
            direction=COLUMN, alignment=CENTER, flex=1))
        self.code_textbox = toga.MultilineTextInput(
            value="""import os
print(os.getcwd())
if not os.path.isdir('test'):
    os.mkdir('test')
f=open('test.txt', 'w')
f.write('something')
f.close()""",
            style=Pack(padding=5, flex=1))
        c1.add(self.code_textbox)
        c2 = toga.Box(style=Pack(
            direction=COLUMN, alignment=CENTER, flex=1))
        self.output_textbox = toga.MultilineTextInput(
            readonly=True, style=Pack(padding=5, flex=1))
        c2.add(self.output_textbox)
        b2.add(c1)
        b2.add(c2)
        #
        self.main_box.add(b)


class InterpreterLayoutApp(AbstractApp, toga.App):
    """A toga App class that has a layout.

    The layout class will create UI elements and its main_box will be added
    as the app main window's content.
    """

    def __init__(self, formal_name: str, app_id: str, layout: InterpreterLayout):

        super(InterpreterLayoutApp, self).__init__(layout=layout,
                                                   formal_name=formal_name,
                                                   app_id=app_id,
                                                   )
        self.layout = layout

    def startup(self):
        """Construct and show the Toga application.

        It also call the layout build and bind the serivices handlers
        to UI elements on_press call back, if their ids correspond to
        an id in ServiceRegistry.
        """
        self.main_window = toga.MainWindow(title=self.formal_name)
        #
        self.on_begin()
        #
        self.main_window.content = self.layout.main_box  # type: ignore
        #
        self.main_window.show()  # type: ignore

    def on_exit(self):
        self.on_end()
        return True
