import sys
import os
import Scripts
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

import Scripts.niftiToBids
import Scripts.runPipeline
import Scripts.runQC
import Scripts.setupPipeline

VERSION = '''0.0.1'''

# class DSIButton():
#     def __init__(self, qButton: QPushButton, name: str, action: function):
#         self.name = name
#         self.button = qButton
#         self.action = action

#     def doAction(self):
#         print(f'DEBUG: Beginning action: {self.action} for button named: {self.name}')
#         self.action()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"DSI Studio Pipeline")
        self.Xstart = 300
        self.WIDTH = 1200
        self.Ystart = 200
        self.HEIGHT = 600
        self.setGeometry(self.Xstart, self.Ystart, self.WIDTH, self.HEIGHT)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        self.label = QLabel("Welcome!", self)
        self.label.setFont(QFont("Serif", 20))
        self.label.setStyleSheet(
            "color: #642727;"
            "font-weight: bold;"
            )
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.label)

        ### make setup button
        if os.path.isdir('convertToBids'):
            # only refresh images if directory setup already is complete
            self.setupButton = QPushButton("Pull Singularity images (create or update)")
            self.setupAction = Scripts.setupPipeline.UpdateImages
        else:
            self.setupButton = QPushButton("Set up directories")
            self.setupAction = Scripts.setupPipeline.main
        self.setupButton.clicked.connect(self.setupButtonClick)
        self.setupButton.setFixedSize(650, 50)
        layout.addWidget(self.setupButton)

        ### make nifti button
        self.niftiButton = QPushButton("Move nifti files to BIDS directory")
        self.niftiButton.clicked.connect(self.niftiButtonClick)
        self.niftiButton.setFixedSize(650, 50)
        layout.addWidget(self.niftiButton)

        ### make mriqc button
        self.mriqcButton = QPushButton("Run MRIQC for anatomical data")
        self.mriqcButton.clicked.connect(self.mriqcButtonClick)
        self.mriqcButton.setFixedSize(650, 50)
        layout.addWidget(self.mriqcButton)

        ### make src button
        self.srcButton = QPushButton("Run DSI Studio src action for diffusion data")
        self.srcButton.clicked.connect(self.srcButtonClick)
        self.srcButton.setFixedSize(650, 50)
        layout.addWidget(self.srcButton)

        ### make rec button
        self.recButton = QPushButton("Run DSI Studio rec action for diffusion data")
        self.recButton.clicked.connect(self.recButtonClick)
        self.recButton.setFixedSize(650, 50)
        layout.addWidget(self.recButton)
        ### end buttons
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.createMenuBar()
        self.statusBar().showMessage(f"Running DSI Studio Pipeline and Visualizer App Version: {VERSION}")
    ### END __init__()

    def setupButtonClick(self)->None:
        self.label.setText("Attempting to set up directories...")
        self.setupAction() # determined when button is initialized
        self.label.setText("Setup complete!")
        self.makeButtonInactive(self.setupButton)
    
    def niftiButtonClick(self)->None:
        self.label.setText("Moving nifti files to BIDS format...")
        Scripts.niftiToBids.NiftiToBIDS()
        self.label.setText("BIDS re-format complete!")
        self.makeButtonInactive(self.niftiButton)

    def mriqcButtonClick(self)->None:
        self.label.setText("Running MRIQC...")
        Scripts.runQC.RunMRIQC()
        self.label.setText("MRIQC Complete!")
        self.makeButtonInactive(self.mriqcButton)

    def srcButtonClick(self)->None:
        self.label.setText("Running SRC action")
        Scripts.runPipeline.RunSRC()
        self.label.setText("SRC Complete!")
        self.makeButtonInactive(self.srcButton)

    def recButtonClick(self)->None:
        self.label.setText("Running REC action")
        Scripts.runPipeline.RunREC()
        self.label.setText("REC Complete!")
        self.makeButtonInactive(self.recButton)

    def makeButtonInactive(self, button:QPushButton)->None:
        '''
        Disable any QPushButton
        '''
        button.setDisabled(True)
        button.setToolTip("Action already complete!")

    def createMenuBar(self)->None:
        '''
        Add menu bar dropdowns and tools here.
        '''
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")

        exitAction = fileMenu.addAction("Exit")
        exitAction.triggered.connect(self.close)
        


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()