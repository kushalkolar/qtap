#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import inspect
from builtins import int, float, str, bool
from typing import *
from collections import namedtuple


widget_mapping = {
    int: QtWidgets.QSpinBox,
    float: QtWidgets.QDoubleSpinBox,
    bool: QtWidgets.QCheckBox,
    str: QtWidgets.QLineEdit,
}

val_setters = {
    QtWidgets.QSpinBox: "setValue",
    QtWidgets.QDoubleSpinBox: "setValue",
    QtWidgets.QCheckBox: "setChecked",
    QtWidgets.QLineEdit: "setText",
}


class Arg:
    acceptable_types = (int, float, str, bool)
    sig_changed = QtCore.pyqtSignal(object)

    def __init__(
        self,
        name: str,
        typ: type,
        val: Union[int, float, str, bool],
        parent: QtWidgets.QWidget,
        vlayout: QtWidgets.QVBoxLayout,
    ):
        """
        Creates the appropriate QWidget interface.

        Parameters
        ----------
        name : str
            argument name

        typ : type
            function type, one of ``int``, ``float``, ``str`` or ``bool``.
            Used for determining the correct QWidget to be used

        val : Union[int, float, str, bool]
            default value for the widget

        parent : QtWidgets.QWidget
            parent widget

        vlayout : QtWidgets.QVBoxLayout
            parent VBoxLayout
        """
        self.parent = parent
        self.vlayout = vlayout

        self.hlayout = QtWidgets.QHBoxLayout()

        self._qlabel = QtWidgets.QLabel(self.parent)
        self.hlayout.addWidget(self._qlabel)
        self.name = name

        self.typ = typ

        self.widget = widget_mapping[self.typ](self.parent)
        self.hlayout.addWidget(self.widget)

        self.val = val

        self.vlayout.addLayout(self.hlayout)

        if self.typ is str:
            self.widget.textEdited.connect(lambda v: setattr(self, '_val', v))
        elif self.typ is bool:
            self.widget.toggled.connect(lambda v: setattr(self, '_val', v))

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, n):
        self._name = n
        self._qlabel.setText(self._name)

    @property
    def val(self) -> Union[int, float, str, bool]:
        return self._val

    @val.setter
    def val(self, v: Union[int, float, str, bool]):
        if v is None:
            self._val = v
            return

        assert isinstance(v, self.acceptable_types)

        self._val = v

        # use the correct func to set the value based on type
        getattr(self.widget, val_setters[type(self.widget)])(self.val)

    def __repr__(self):
        return f"name:\t{self.name}\n" f"val:\t{self.val}\n" f"typ:\t{self.typ}"


class ArgNumeric(Arg):
    acceptable_types = (int, float)

    def __init__(
        self,
        name: str,
        typ: type,
        val: Union[int, float],
        parent: QtWidgets.QWidget,
        vlayout: QtWidgets.QVBoxLayout,
        minmax: tuple,
        step: Union[int, float],
        use_slider: bool = False,
        suffix: str = None,
    ):
        """
        Creates numerical QWidget interface

        Parameters
        ----------
        minmax : tuple
            min & max values

        step : Union[int, float]
            step size for the spin box

        use_slider : Optional[bool]
            adds a slider below the spin box

        suffix : Optional[str]
            text suffix for the spin box, like data units
        """
        super().__init__(name, typ, val, parent, vlayout)

        self.slider = None

        self.minmax = minmax

        self.step = step

        if use_slider:
            self.slider = QtWidgets.QSlider(self.parent)
            self.slider.setOrientation(QtCore.Qt.Horizontal)
            self.slider.setMaximum(self.max)
            self.slider.setMinimum(self.min)
            self.widget.valueChanged.connect(self.slider.setValue)
            self.slider.valueChanged.connect(self.widget.setValue)
            self.vlayout.addWidget(self.slider)

        self.suffix = suffix
        if self.suffix is not None:
            self.widget.setSuffix(self.suffix)

        self.widget.valueChanged.connect(lambda v: setattr(self, '_val', v))
        self.val = val

    def set_slider(self):
        if self.slider is not None:
            self.slider.setMaximum(self.max)
            self.slider.setMinimum(self.min)

    @property
    def minmax(self) -> tuple:
        return tuple(self._minmax)

    @minmax.setter
    def minmax(self, minmax: tuple):
        self._minmax = list(minmax)
        self.min = self.minmax[0]
        self.max = self.minmax[1]

    @property
    def min(self) -> Union[int, float]:
        return self._min

    @min.setter
    def min(self, v: Union[int, float]):
        assert isinstance(v, (int, float))
        self._min = v
        self._minmax[0] = v

        self.widget.setMinimum(v)
        self.set_slider()

    @property
    def max(self) -> Union[int, float]:
        return self._max

    @max.setter
    def max(self, v: Union[int, float]):
        assert isinstance(v, (int, float))
        self._max = v
        self._minmax[1] = v

        self.widget.setMaximum(v)
        self.set_slider()

    @property
    def step(self) -> Union[int, float]:
        return self._step

    @step.setter
    def step(self, v: Union[int, float]):
        assert isinstance(v, (int, float))
        self._step = v
        self.widget.setSingleStep(v)

    def __repr__(self):
        return (
            f"{super(ArgNumeric, self).__repr__()}\n"
            f"minmax:\t{self.minmax}\n"
            f"step:\t{self.step}\n"
            f"suffix:\t{self.suffix}"
        )


def _get_argument(sig: inspect.Parameter, parent, vlayout, **kwargs):
    if sig.default is inspect._empty:
        default = None
    else:
        default = sig.default

    if sig.annotation in [int, float]:
        return ArgNumeric(
            name=sig.name,
            typ=sig.annotation,
            val=default,
            parent=parent,
            vlayout=vlayout,
            **kwargs,
        )

    else:
        return Arg(
            name=sig.name,
            typ=sig.annotation,
            val=default,
            parent=parent,
            vlayout=vlayout,
        )


class Function:
    def __init__(
        self,
        func: callable,
        overrides: dict = None,
        parent: Optional[QtWidgets.QWidget] = None,
        kwarg_entry: bool = False,
    ):
        """
        Creates a widget based on the function signature

        Parameters
        ----------
        func : callable
            A function with type annotations

        overrides : dict
            Not yet implemented, may not every implement.
            Easier to just access the arguments to manually set custom things anyways

        parent : Optional[QtWidgets.QWidget]
            parent QWidget

        kwarg_entry : bool
            include a text box for kwargs entry
        """
        self.widget = QtWidgets.QWidget(parent)

        self.vlayout = QtWidgets.QVBoxLayout(self.widget)

        self.overrides = overrides

        self.name = func.__name__
        self._qlabel = QtWidgets.QLabel(self.widget)
        self._qlabel.setStyleSheet("font-weight: bold")
        self.vlayout.addWidget(self._qlabel)

        arg_names = inspect.signature(func).parameters.keys()
        arg_sigs = inspect.signature(func).parameters.values()

        Arguments = namedtuple("Arguments", arg_names)
        self.arguments = Arguments(
            *(
                _get_argument(
                    sig,
                    parent=self.widget,
                    vlayout=self.vlayout,
                    minmax=(0, 999),
                    step=1,
                )
                for sig in arg_sigs
            )
        )

    def add_arg(self):
        pass

    def get_data(self):
        return {arg.name: arg.val for arg in self.arguments}

    def set_data(self, d: dict):
        for arg in d.keys():
            getattr(self.arguments, arg).val = d[arg]
