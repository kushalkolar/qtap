from PyQt5 import QtWidgets
from qtap.core import Function
from inspect import signature
from pyqtgraph.console import ConsoleWidget


def detrend_df_f(quantileMin: float = 8, frames_window: int = 500,
                 flag_auto: bool = True,
                 use_fast: bool = False,
                 use_residuals: bool = True,
                 detrend_only: bool = False):
    pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    # w = QtWidgets.QWidget()
    # vlayout = QtWidgets.QVBoxLayout(w)
    #
    # func = detrend_df_f

    func = Function(detrend_df_f)
    func.widget.show()

    print(func.get_data())

    console = ConsoleWidget(parent=func.widget, namespace={'this': func})
    func.vlayout.addWidget(console)

    # for param in signature(func).parameters.values():
    #     arg = get_argument(param, parent=w, vlayout=vlayout, minmax=(0, 9999), step=1, use_slider=True)
    # w.show()

    app.exec()