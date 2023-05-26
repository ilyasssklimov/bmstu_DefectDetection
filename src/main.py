from PyQt5 import QtWidgets
import sys
sys.path.append('..')

from src.app.window import Window


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
