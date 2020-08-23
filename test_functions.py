from PyQt5 import QtWidgets
from qtap import Functions
from pyqtgraph.console import ConsoleWidget


def func_A(a: int = 1, b: float = 3.14, c: str = 'yay', d: bool = True):
    pass


def func_B(x: float = 50, y: int = 2.7, u: str = 'bah'):
    pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

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
                },

            'c': {'ignore': True}
        }

    functions = Functions(
        functions=[func_A, func_B],
        arg_opts=[opts_A, None],
        scroll=False,
        orient='V'
    )

    console = ConsoleWidget(parent=functions, namespace={'this': functions})
    functions.main_layout.addWidget(console)
    functions.sig_changed.connect(print)

    functions.show()

    app.exec()
