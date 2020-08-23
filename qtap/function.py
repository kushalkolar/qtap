#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import inspect
from typing import *
from collections import namedtuple
from functools import partial
from .argument import Arg, ArgNumeric


def _get_argument(sig: inspect.Parameter, parent, vlayout, **opts):
    if sig.default is inspect._empty:
        default = None
    else:
        default = sig.default

    kwargs = dict(
        name=sig.name,
        typ=sig.annotation,
        val=default,
        parent=parent,
        vlayout=vlayout
    )

    kwargs.update(opts)

    if sig.annotation in [int, float]:
        return ArgNumeric(**kwargs)

    else:
        return Arg(**kwargs)


# this is a massive nested lambda, not sure if there's a more elegant way to do this without a nasty loop
_ignore_arguments = lambda d: (lambda d: True if d['ignore'] else False)(d) if 'ignore' in d.keys() else False


class Function(QtCore.QObject):
    # emit the entire dict
    sig_changed = QtCore.pyqtSignal(dict)
    sig_set_clicked = QtCore.pyqtSignal(dict)

    # emits the name of the arg and its value
    sig_arg_changed = QtCore.pyqtSignal(str, object)

    def __init__(
            self,
            func: callable,
            arg_opts: dict = None,
            parent: Optional[QtWidgets.QWidget] = None,
            kwarg_entry: bool = False,
    ):
        """
        Creates a widget based on the function signature

        Parameters
        ----------
        func : callable
            A function with type annotations

        arg_opts : dict
            manually set certain features of an Arg

        parent : Optional[QtWidgets.QWidget]
            parent QWidget

        kwarg_entry : bool
            Not yet implemented.
            include a text box for kwargs entry


        Attributes
        -------
        sig_changed : dict
            Emitted when an argument value changes.
            Emits dict for all function arguments.
            See ``get_data()`` for details on the dict.

        sig_set_clicked : dict
            Emitted when the "Set" button is clicked.
            Emits dict for all function arguments.
            See ``get_data()`` for details on the dict.

        sig_arg_changed : str, object
            Emitted when specific argument value changes.
            Emits argument name and argument value


        Examples
        --------

        **Basic**

        .. code-block:: python
            :linenos:

            from PyQt5 import QtWidgets
            from qtap import Function

            # annotated function
            def f(a: int = 1, b: float = 3.14, c: str = 'yay', d: bool = True):
                pass

            app = QtWidgets.QApplication([])

            # basic
            func = Function(f)
            func.widget.show()

            app.exec()

        **Opt Args**

        .. code-block:: python
            :linenos:

            from PyQt5 import QtWidgets
            from qtap import Function
            from pyqtgraph.console import ConsoleWidget


            def f(a: int = 1, b: float = 3.14, c: str = 'yay', d: bool = True):
                pass


            if __name__ == '__main__':
                app = QtWidgets.QApplication([])

                # opt args dict
                opts = \
                    {
                        'b':
                            {
                                'use_slider': True,
                                'minmax': (0, 100),
                                'step': 1,
                                'suffix': '%',
                                'typ': int,
                                'tooltip': 'yay tooltips'
                            }
                    }

                func = Function(f, arg_opts=opts)
                func.widget.show()

                console = ConsoleWidget(parent=func.widget, namespace={'this': func})
                func.vlayout.addWidget(console)

                app.exec()


        """
        super(Function, self).__init__(parent)

        self.widget = QtWidgets.QWidget(parent)

        self.vlayout = QtWidgets.QVBoxLayout(self.widget)

        self.callable = func

        self.name = self.callable.__name__
        self._qlabel = QtWidgets.QLabel(self.widget)
        self._qlabel.setStyleSheet("font-weight: bold")
        self._qlabel.setText(self.name)
        self.vlayout.addWidget(self._qlabel)

        arg_names = inspect.signature(func).parameters.keys()
        arg_sigs = inspect.signature(func).parameters.values()

        self.arg_opts = dict.fromkeys(arg_names)
        self.arg_opts = {arg: {} for arg in arg_names}
        if arg_opts is not None:
            self.arg_opts.update(arg_opts)

        ignore = [
            k for k in self.arg_opts.keys() if _ignore_arguments(self.arg_opts[k])
        ]

        arg_names = [n for n in arg_names if n not in ignore]

        # Add all the arguments as named tuples
        # so they're accessible like attributes
        # dynamically named based on the args from the function!
        Arguments = namedtuple("Arguments", arg_names)
        self.arguments = Arguments(
            *(
                _get_argument(
                    sig,
                    parent=self.widget,
                    vlayout=self.vlayout,
                    **self.arg_opts[sig.name]
                )
                for sig in arg_sigs if sig.name not in ignore
            )
        )

        # button at the bottom, sends a "set" signal when clicked
        self.button_set = QtWidgets.QPushButton(self.widget)
        self.button_set.setText('Set')
        self.vlayout.addWidget(self.button_set)
        self.button_set.clicked.connect(
            partial(self._emit_data, self.sig_set_clicked)
        )

        for arg in self.arguments:
            # emit entire dict when arg is changed
            arg.sig_changed.connect(
                partial(self._emit_data, self.sig_changed)
            )

            # also emit just arg.name and arg.val when changed
            arg.sig_changed.connect(
                partial(self.sig_arg_changed.emit, arg.name)
            )

    def _emit_data(self, sig: QtCore.pyqtBoundSignal):
        sig.emit(self.get_data())

    def get_data(self) -> Dict[str, object]:
        """
        Get the data from the function arguments

        Returns
        -------
        dict
            dict keys are the argument names, dict values are the argument vals

        """

        return {arg.name: arg.val for arg in self.arguments}

    def set_data(self, d: dict):
        for arg in d.keys():
            getattr(self.arguments, arg).val = d[arg]

    def set_title(self, title: str):
        """
        Set the title text for the function. The default title is the function name.

        Parameters
        ----------
        title : str
            Title to display above the widgets for this function

        Returns
        -------
        None

        """
        self._qlabel.setText(title)

    def __repr__(self):
        return f'{self.name}' \
                   f'\n' + \
            '\n'.join(
                [
                    f'  {arg.name}:\n' \
                        f'    {arg.typ}\n' \
                        f'    {arg.val}'
                    for arg in self.arguments
                ]
            )


class Functions(QtWidgets.QWidget):
    sig_changed = QtCore.pyqtSignal(dict)
    sig_set_clicked = QtCore.pyqtSignal(dict)

    def __init__(
            self,
            functions: List[callable],
            arg_opts: Optional[List[dict]] = None,
            parent: Optional[QtWidgets.QWidget] = None,
            scroll: bool = False,
            orient: str = 'V',
            columns: bool = False,
            **kwargs
    ):
        """

        Parameters
        ----------
        functions : List[callable]
            list of functions

        arg_opts : List[dict], optional
            optional list of dicts to manually set features of an argument.
            passed to ``Function``

        parent : QtWidgets.QWidget, optional
            parent widget

        scroll : bool
            Not yet implemented

        orient : str
            orientation of the individual functions. One of ``V`` or ``H``.
            Default orientation is ``V`` (vertical)

        columns : bool
            Not yet implemented

        **kwargs
            passed to QtWidgets.QWidget.__init__()

        Attributes
        -------
        sig_changed : dict
            Emitted when an underlying function emits sig_changed().
            The emitted dict comes from ``get_data()``,
            see the docstring for ``get_data()`` for details.

        sig_set_clicked : dict
            Emitted when an underlying function emits sig_set_clicked().
            The emitted dict comes from ``get_data()``,
            see the docstring for ``get_data()`` for details.

        Examples
        --------

        **Basic**

        .. code-block:: python
            :linenos:

            from PyQt5 import QtWidgets
            from qtap import Functions
            from pyqtgraph.console import ConsoleWidget


            def func_A(a: int = 1, b: float = 3.14, c: str = 'yay', d: bool = True):
                pass


            def func_B(x: float = 50, y: int = 2.7, u: str = 'bah'):
                pass


            if __name__ == '__main__':
                app = QtWidgets.QApplication([])

                functions = Functions([func_A, func_B])

                console = ConsoleWidget(parent=functions, namespace={'this': functions})
                functions.main_layout.addWidget(console)

                functions.show()

                app.exec()

        **Opt Args**

        .. code-block:: python
            :linenos:

            from PyQt5 import QtWidgets
            from qtap import Functions
            from pyqtgraph.console import ConsoleWidget


            def func_A(a: int = 1, b: float = 3.14, c: str = 'yay', d: bool = True):
                pass


            def func_B(x: float = 50, y: int = 2.7, u: str = 'bah'):
                pass


            if __name__ == '__main__':
                app = QtWidgets.QApplication([])

                # opt args for ``func_A``
                opts_A = \
                    {
                        'b':
                            {
                                'use_slider': True,
                                'minmax': (0, 100),
                                'step': 1,
                                'suffix': '%',
                                'typ': int,
                                'tooltip': 'yay tooltips'
                            }
                    }

                # functions where one has ``opt_args``
                functions = Functions(
                    functions=[func_A, func_B],
                    arg_opts=[opts_A, None], # opt_args in same order as functions
                )

                console = ConsoleWidget(parent=functions, namespace={'this': functions})
                functions.main_layout.addWidget(console)

                functions.show()

                app.exec()

        """
        super().__init__(parent, **kwargs)

        _functions = namedtuple(
            'Functions',
            [f.__name__ for f in functions]
        )

        if arg_opts is None:
            arg_opts = [None] * len(functions)

        self.functions = _functions(
            *(
                Function(
                    func,
                    opt,
                    parent=self
                )
                for func, opt in zip(functions, arg_opts)
            )
        )

        if scroll:
            self.vlayout = QtWidgets.QVBoxLayout(self)

            self.scroll_area = QtWidgets.QScrollArea(self)
            self.vlayout.addWidget(self.scroll_area)
            self.scroll_area.setWidgetResizable(True)

            self.scroll_content = QtWidgets.QWidget(self.scroll_area)
            self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
            self.scroll_content.setLayout(self.scroll_layout)

            self.main_layout = self.scroll_layout
        else:
            if orient in ['V', 'vertical']:
                self.main_layout = QtWidgets.QVBoxLayout(self)
            elif orient in ['H', 'horizontal']:
                self.main_layout = QtWidgets.QHBoxLayout(self)

        f: Function
        for f in self.functions:
            self.main_layout.addWidget(f.widget)

            # emit dict when any function changes
            f.sig_changed.connect(
                partial(self._emit_data, self.sig_changed)
            )

            # emit dict when any function is set
            f.sig_set_clicked.connect(
                partial(self._emit_data, self.sig_set_clicked)
            )

    def _emit_data(self, sig):
        sig.emit(self.get_data())

    def get_data(self) -> Dict[callable, dict]:
        """

        Returns
        -------
            dict
                dict keys are the functions, each dict values is a kwargs dict

        """
        return {f.callable: f.get_data() for f in self.functions}

    def __repr__(self):
        return '\n'.join(
            [
                f.__repr__() for f in self.functions
            ]
        )
