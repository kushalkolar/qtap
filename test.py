from PyQt5 import QtWidgets
from qtap.core import Function
from pyqtgraph.console import ConsoleWidget


def detrend_df_f(quantileMin: float,
                 text: str,
                 frames_window: int = 500,
                 flag_auto: bool = True,
                 use_fast: bool = False,
                 use_residuals: bool = True,
                 detrend_only: bool = False,
                 string_test: str = 'bah'):
    pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    func = Function(detrend_df_f)
    func.widget.show()

    console = ConsoleWidget(parent=func.widget, namespace={'this': func})
    func.vlayout.addWidget(console)

    app.exec()
