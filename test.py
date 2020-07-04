from PyQt5 import QtWidgets
from qtap.core import get_argument
from inspect import signature


def detrend_df_f(quantileMin: float = 8, frames_window: int = 500,
                 flag_auto: bool = True,
                 use_fast: bool = False,
                 use_residuals: bool = True,
                 detrend_only: bool = False):
    pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    w = QtWidgets.QWidget()
    vlayout = QtWidgets.QVBoxLayout(w)

    func = detrend_df_f

    for param in signature(func).parameters.values():
        arg = get_argument(param, parent=w, minmax=(0, 100), step=1)
        vlayout.addLayout(arg.hlayout)

    w.show()

    app.exec()