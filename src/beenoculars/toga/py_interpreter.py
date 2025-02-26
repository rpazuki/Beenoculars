import logging
from abc import abstractmethod

import toga
from toga.style import Pack
from toga.style.pack import CENTER, COLUMN, ROW

from beenoculars.core import AbstractApp, AbstractLayout
from beenoculars.core.__safe_calls__ import __chain_traceback as chain_traceback

log = logging.getLogger(__name__)


class InterpreterLayout(AbstractLayout):
    def __init__(self):
        super(InterpreterLayout, self).__init__()
        self._main_box = None

    @property
    def main_box(self):
        return self._main_box

    def build_layout(self):
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

        def clear_output(widget):
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
                self.output_textbox.value += "---------\n" + out
            except Exception as e:
                self.output_textbox.value += "---------\n" + \
                    f"Error: \n {e}{chain_traceback(e.__traceback__)}"

            self.output_textbox.scroll_to_bottom()

        btn_run = toga.Button("Run", style=Pack(padding=4, font_size=10),
                              on_press=run)
        btn_clear = toga.Button("Clear", style=Pack(padding=4, color='red', font_size=10),
                                on_press=clear)
        #

        def change_run_font(widget):
            self.code_textbox.style.update(
                font_size=widget.value
            )
            self.line_num_textbox.style.update(
                font_size=widget.value,
                width=int(35*widget.value/14)
            )
        sl_run_font_size = toga.Selection(
            items=[8, 10, 12, 14, 16, 18, 20, 24, 28, 32], value=14,
            on_change=change_run_font,
            style=Pack(padding=4, width=50, font_size=10))
        #
        btn_output_clear = toga.Button("Clear out",
                                       style=Pack(
                                           padding=4, color='red', font_size=10),
                                       on_press=clear_output)

        def change_output_font(widget):
            self.output_textbox.style.update(
                font_size=widget.value
            )
        sl_output_font_size = toga.Selection(
            items=[8, 10, 12, 14, 16, 18, 20, 24, 28, 32], value=14,
            on_change=change_output_font,
            style=Pack(padding=4, width=50, font_size=10))
        #
        b1.add(btn_run)
        b1.add(btn_clear)
        b1.add(sl_run_font_size)
        b1.add(btn_output_clear)
        b1.add(sl_output_font_size)
        #
        b2 = toga.Box(style=Pack(
            direction=COLUMN, alignment=CENTER, flex=1))
        b.add(b2)
        ##
        c1 = toga.Box(style=Pack(
            direction=COLUMN, alignment=CENTER, flex=2))

        c1r1 = toga.Box(style=Pack(
            direction=ROW, alignment=CENTER, flex=1))
        c1.add(c1r1)
        self.line_num_textbox = toga.MultilineTextInput(value="".join(
            [f"{i+1}\n" for i in range(100)]), readonly=True,
            style=Pack(width=35, color='red', padding=0, font_size=14))
        c1r1.add(self.line_num_textbox)
        self.code_textbox = toga.MultilineTextInput(
            value="""import os
print(os.getcwd())
if not os.path.isdir('test'):
    os.mkdir('test')
f=open('test.txt', 'w')
f.write('something')
f.close()""",
            style=Pack(padding=0, font_size=14, flex=1))
        c1r1.add(self.code_textbox)
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
        self.main_window.content = self.layout.main_box
        #
        self.main_window.show()

    def on_exit(self):
        self.on_end()
        return True
