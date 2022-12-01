from main import Ui_RecursiveSearch
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
import sys
from ui_config import Presets


class StartUtility(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.utility = Window()
        self.utility.show()


class Window(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_RecursiveSearch()
        self.ui.setupUi(self)
        # self.ui.dragFrame.mouseMoveEvent = self.mouseMoveEvent
        # self.dragPos = QtCore.QPoint()
        self.setWindowIcon(QIcon('images/icon.png'))
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        Presets.start(self)

    # def mousePressEvent(self, event):
    #     self.dragPos = event.globalPos()
    #
    # def mouseMoveEvent(self, event):
    #     if event.buttons() == QtCore.Qt.LeftButton:
    #         self.move(self.pos() + event.globalPos() - self.dragPos)
    #         self.dragPos = event.globalPos()
    #         event.accept()


if __name__ == "__main__":
    app = StartUtility(sys.argv)
    sys.exit(app.exec_())
