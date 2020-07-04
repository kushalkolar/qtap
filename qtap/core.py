#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtWidgets
from inspect import signature, Parameter
from builtins import int, float, str, bool
from typing import *

widget_mapping = \
    {
        int:    QtWidgets.QSpinBox,
        float:  QtWidgets.QDoubleSpinBox,
        bool:   QtWidgets.QCheckBox,
        str:    QtWidgets.QLineEdit
    }

val_setters = \
    {
        QtWidgets.QSpinBox:         'setValue',
        QtWidgets.QDoubleSpinBox:   'setValue',
        QtWidgets.QCheckBox:        'setChecked',
        QtWidgets.QLineEdit:        'setText'
    }


class BaseArg:
    acceptable_types = (int, float, str, bool)

    def __init__(
            self,
            name: str,
            annot: type,
            val: Union[int, float, str, bool],
            parent: QtWidgets.QWidget
    ):
        self.hlayout = QtWidgets.QHBoxLayout()
        self.parent = parent

        self._qlabel = QtWidgets.QLabel(self.parent)
        self.hlayout.addWidget(self._qlabel)
        self.name = name

        self.annot = annot

        self.widget = widget_mapping[self.annot](self.parent)
        self.hlayout.addWidget(self.widget)

        self.val = val

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
        assert isinstance(v, self.acceptable_types)

        self._val = v

        # use the correct func to set the value based on type
        getattr(self.widget, val_setters[type(self.widget)])(self.val)


class ArgNumeric(BaseArg):
    acceptable_types = (int, float)

    def __init__(self, name: str, annot: type, val: Union[int, float, str, bool], parent: QtWidgets.QWidget,  minmax: tuple, step: Union[int, float], suffix: str = None):
        super().__init__(name, annot, val, parent)

        self.minmax = minmax

        self.min = self.minmax[0]
        self.max = self.minmax[1]

        self.suffix = suffix
        if self.suffix is not None:
            self.widget.setSuffix(self.suffix)

    @property
    def minmax(self) -> tuple:
        return self._minmax

    @minmax.setter
    def minmax(self, minmax: tuple):
        self._minmax = minmax
        self.min = self.minmax[0]
        self.max = self.minmax[1]

    @property
    def min(self) -> Union[int, float]:
        return self._min

    @min.setter
    def min(self, v: Union[int, float]):
        assert isinstance(v, (int, float))
        self._min = v
        self.widget.setMinimum(v)

    @property
    def max(self) -> Union[int, float]:
        return self._max

    @max.setter
    def max(self, v: Union[int, float]):
        assert isinstance(v, (int, float))
        self._max = v
        self.widget.setMaximum(v)

    @property
    def step(self) -> Union[int, float]:
        return self._step

    @step.setter
    def step(self, v: Union[int, float]):
        assert isinstance(v, (int, float))
        self._step = v
        self.widget.setSingleStep(v)


def get_argument(sig: Parameter, parent, minmax, step, suffix: Optional[str] = None):
    if sig.annotation in [int, float]:
        return ArgNumeric(
            name=sig.name,
            annot=sig.annotation,
            val=sig.default,
            parent=parent,
            minmax=minmax,
            step=step,
            suffix=suffix
        )
    else:
        return BaseArg(
            name=sig.name,
            annot=sig.annotation,
            val=sig.default,
            parent=parent
        )

class Function:
    pass
