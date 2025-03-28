from DataSetsAnalysis import work_DataSetsAnalysis
from LoadExperiments import work_LoadExperiments
import sys
import ctypes
from ctypes import byref, c_int32
from PyQt5 import Qt
from qtpy import QtWidgets
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGroupBox, QHBoxLayout, QLabel, QFileDialog, QLineEdit, QPushButton

class MainWindow(Qt.QWidget):
    ''' Main Window '''

    def __init__(self):
        super(MainWindow, self).__init__()
        self.layout = Qt.QVBoxLayout(self)

        self.setGeometry(650, 20, 450, 100)
        self.setWindowTitle("Kapil's Graphical User Interface")

        # Add objects to main window
        self.text_box = QLineEdit(self)
        self.text_box.setPlaceholderText("Enter text here...")
        self.text_box.setText("S:/Users/Maria/DataTENG/ExpResistance/")
        self.layout.addWidget(self.text_box)

        # start Button
        self.btnLE = Qt.QPushButton("LoadExperiments")
        self.layout.addWidget(self.btnLE)

        # load Button
        self.btnDSA = Qt.QPushButton("DataSetsAnalysis")
        self.layout.addWidget(self.btnDSA)

        # Connect the button to a method
        self.btnLE.clicked.connect(self.LoadExperiments)
        self.btnDSA.clicked.connect(self.DataSetsAnalysis)

        self.text_box_log = QLabel("Put the path in the box: S:/Users/Maria/DataTENG/ExpResistance/")
        self.layout.addWidget(self.text_box_log)

    def DataSetsAnalysis(self):
        self.text_box_log.setText("Loading DataSets Analysis...")
        try:
            text = self.text_box.text()
            work_DataSetsAnalysis(text)
            self.text_box_log.setText("Finished Data Sets Analysis")
        except:
            self.text_box_log.setText("Please close the PDF")

    def LoadExperiments(self):
        self.text_box_log.setText("Loading Data...")
        try:
            text = self.text_box.text()
            work_LoadExperiments(text)
            self.text_box_log.setText("Finished Load Experiments")
            time.sleep(1)
            self.text_box_log.setText("Go to: S:/Users/Maria/DataTENG/[Experiment folder of the day]/Reports")

        except:
            self.text_box_log.setText("Please close the PDF")



def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
# work_LoadExperiments('S:/Users/Maria/DataTENG/ExpResistance/')
# work_DataSetsAnalysis('S:/Users/Maria/DataTENG/ExpMotorParameters/')
