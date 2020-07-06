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

    kwargs = dict(name=sig.name,
                  typ=sig.annotation,
                  val=default,
                  parent=parent,
                  vlayout=vlayout)

    kwargs.update(opts)

    if sig.annotation in [int, float]:
        return ArgNumeric(**kwargs)

    else:
        return Arg(**kwargs)


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

        Examples
        --------

        .. code-block:: python
            from PyQt5 import QtWidgets
            from qtap import Function

            # annotated function
            def f(a: int = 1, b: float = 3.14, c: str = 'yay', d: bool = True):
                pass

            app = QtWidgets.QApplication([])

            # basic
            func = Function(f)
            func.widget.show()

            # some arg_opts
            opts = \
                {
                    'b':
                        {
                            'use_slider': True,
                            'minmax': (0, 100),
                            'step': 0.5,
                            'suffix': '%'
                        }
                }

            app.exec()

        """
        super(Function, self).__init__(parent)

        self.widget = QtWidgets.QWidget(parent)

        self.vlayout = QtWidgets.QVBoxLayout(self.widget)

        self.name = func.__name__
        self._qlabel = QtWidgets.QLabel(self.widget)
        self._qlabel.setStyleSheet("font-weight: bold")
        self._qlabel.setText(self.name)
        self.vlayout.addWidget(self._qlabel)

        arg_names = inspect.signature(func).parameters.keys()
        arg_sigs = inspect.signature(func).parameters.values()

        self.arg_opts = dict.fromkeys(arg_names)
        self.arg_opts = {arg: {} for arg in arg_names}
        self.arg_opts.update(arg_opts)

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
                for sig in arg_sigs
            )
        )

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

    def get_data(self):
        return {arg.name: arg.val for arg in self.arguments}

    def set_data(self, d: dict):
        for arg in d.keys():
            getattr(self.arguments, arg).val = d[arg]
