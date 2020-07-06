from PyQt5 import QtWidgets
from qtap.core import Function
from pyqtgraph.console import ConsoleWidget


def f(a: int = 1, b: float = 3.14, c: str = 'yay', d: bool = True):
    pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

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
