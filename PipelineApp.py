import sys
import os
from Scripts.Util import Debug
from Scripts import niftiToBids, runPipeline, runQC, setupPipeline
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QSpacerItem, QSizePolicy, QToolBar
    )
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Dev Options:
VERSION = '''
0.0.2
'''
DEBUG = True
# End Dev Options

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
        self.Xstart = 150
        self.WIDTH = 1500
        self.Ystart = 100
        self.HEIGHT = 750
        self.setGeometry(self.Xstart, self.Ystart, self.WIDTH, self.HEIGHT)
    
        self.makeToolbar() # makes toolbar at top of screen
        self.activateAll() # makes central widget, status and buttons
        
    ### END __init__()

    def setupButtonClick(self)->None:
        self.label.setText("Attempting to set up directories...")
        self.setupAction() # determined when button is initialized
        self.label.setText("Setup complete!")
        self.makeButtonInactive(self.setupButton)
    
    def niftiButtonClick(self)->None:
        self.label.setText("Moving nifti files to BIDS format...")
        niftiToBids.NiftiToBIDS()
        self.label.setText("BIDS re-format complete!")
        self.makeButtonInactive(self.niftiButton)

    def mriqcButtonClick(self)->None:
        self.label.setText("Running MRIQC...")
        runQC.RunMRIQC()
        self.label.setText("MRIQC Complete!")
        self.makeButtonInactive(self.mriqcButton)

    def srcButtonClick(self)->None:
        self.label.setText("Running SRC action")
        runPipeline.RunSRC()
        self.label.setText("SRC Complete!")
        self.makeButtonInactive(self.srcButton)
        return

    def recButtonClick(self)->None:
        self.label.setText("Running REC action")
        runPipeline.RunREC()
        self.label.setText("REC Complete!")
        self.makeButtonInactive(self.recButton)
        return

    def makeToolbar(self)->None:
        # making toolbar widget
        toolbar = QToolBar("ToolBox")
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # buttons
        self.refreshButton  = QPushButton("Refresh")
        self.refreshButton.clicked.connect(self.activateAll)
        self.refreshButton.setFixedSize(60, 60)
        toolbar.setStyleSheet("""
    QToolBar {
        background: #323D3D;
        border: 1px solid #555;
        spacing: 5px;
    }
    QPushButton {
        background: #004242;
        padding: 5px;
    }
    QPushButton:hover {
        background: #002E2E;
    }
""")
        toolbar.addWidget(self.refreshButton)
        
        return

    def activateAll(self)->None:
        Debug.Log(f'Resetting app state', DEBUG)
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget) # main widget

        self.label = QLabel("Welcome!", self)
        self.label.setFont(QFont("Serif", 20))
        self.label.setStyleSheet(
            "color: #642727;"
            "font-weight: bold;"
            )

        # making vertical buttons widget
        vButtons = QVBoxLayout()
        vButtons.addWidget(self.label)

        ### make setup button
        if os.path.isdir('convertToBids'):
            # only refresh images if directory setup already is complete
            self.setupButton = QPushButton("Pull Singularity images (create or update)")
            self.setupAction = setupPipeline.UpdateImages
        else:
            Debug.Log(f'Directories have not yet been set up. Doing that now...', DEBUG)
            self.setupButton = QPushButton("Set up directories")
            self.setupAction = setupPipeline.main
        self.setupButton.clicked.connect(self.setupButtonClick)
        self.setupButton.setFixedSize(int(.6*self.WIDTH), int(.1*self.HEIGHT))
        vButtons.addWidget(self.setupButton)

        ### make nifti button
        self.niftiButton = QPushButton("Move nifti files to BIDS directory")
        self.niftiButton.clicked.connect(self.niftiButtonClick)
        self.niftiButton.setFixedSize(int(.6*self.WIDTH), int(.1*self.HEIGHT))
        vButtons.addWidget(self.niftiButton)

        ### make mriqc button
        self.mriqcButton = QPushButton("Run MRIQC for anatomical data")
        self.mriqcButton.clicked.connect(self.mriqcButtonClick)
        self.mriqcButton.setFixedSize(int(.6*self.WIDTH), int(.1*self.HEIGHT))
        vButtons.addWidget(self.mriqcButton)

        ### make src button
        self.srcButton = QPushButton("Run DSI Studio src action for diffusion data")
        self.srcButton.clicked.connect(self.srcButtonClick)
        self.srcButton.setFixedSize(int(.6*self.WIDTH), int(.1*self.HEIGHT))
        vButtons.addWidget(self.srcButton)

        ### make rec button
        self.recButton = QPushButton("Run DSI Studio rec action for diffusion data")
        self.recButton.clicked.connect(self.recButtonClick)
        self.recButton.setFixedSize(int(.6*self.WIDTH), int(.1*self.HEIGHT))
        vButtons.addWidget(self.recButton)

        layout.addLayout(vButtons)
        
        ### end buttons

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #self.createMenuBar()
        self.statusBar().showMessage(f"Running DSI Studio Pipeline Interface App Version: {VERSION}")
        return None

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