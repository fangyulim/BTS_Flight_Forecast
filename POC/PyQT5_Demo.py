from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout, QPushButton
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QBrush, QColor
import sys

qtCreatorFile = "../PyQt5_GUI_Demo.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class milestone2_v2(QMainWindow):
    def __init__(self):
        super(milestone2_v2, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Business Page
        self.loadStateList()
        self.ui.AirportSelection.currentTextChanged.connect(self.stateChanged)

        self.ui.PredictButton.clicked.connect(self.startPrediction)

    def loadStateList(self):
        self.ui.AirportSelection.clear()
        self.ui.AirportSelection.addItems(['Seattle - SEA', 'New York - JKF', 'San Jose - SJC'])

    def stateChanged(self):
        print(self.ui.AirportSelection.currentText())

    def startPrediction(self):
        airport_selection = self.ui.AirportSelection.currentText()
        date_selection =self.ui.DateSelection.date().toString("yyyy.MM.dd")
        time_selection = self.ui.TimeSelection.time().toString("HH:mm:ss")
        model_response = "calling prediction function with airport:"+ airport_selection+ ", date:"+ date_selection+ ", time:"+ time_selection

        # set test field to value from model
        self.ui.ProbabilityOfDelayResult.setText(model_response)

        if(self.ui.EstimateCheckBox.isChecked()):

            avg_response = "calling avg estimator function with airport:"+ airport_selection+ ", date:"+ date_selection+ ", time:"+ time_selection
            self.ui.AvgDelayResult.setText(model_response)

            self.ui.AvgDelayResult.setVisible(True)
            self.ui.label_6.setVisible(True)
        else:
            self.ui.AvgDelayResult.setVisible(False)
            self.ui.label_6.setVisible(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = milestone2_v2()
    window.show()
    sys.exit(app.exec_())