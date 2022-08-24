from PyQt5 import QtWidgets
from test_main import Ui_MainWindow  # импорт нашего сгенерированного файла
from test import Ui_Form
import sys


# class SearchWindow(QtWidgets.QMainWindow):
#     def __init__(self):
#         super(SearchWindow, self).__init__()
#         self


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #self.ui.pushButton.clicked.connect(self.btnClicked)  # обработчик кнопки pushButton

    # def btnClicked(self):
    #     # a = ['qq', 'ww', 'ee']
    #     # self.ui.label.setText(f'{a[1]}')
    #     # # Если не использовать, то часть текста исчезнет.
    #     # self.ui.label.adjustSize()
    #     self.w = Ui_Form()
    #     self.w.show()


app = QtWidgets.QApplication([])
application = MainWindow()
application.show()

sys.exit(app.exec())