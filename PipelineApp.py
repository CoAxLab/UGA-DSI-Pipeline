import sys
import os
from multiprocessing import Process
from Scripts.Util import Debug, StatusChecker, FetchFiles
from Scripts import niftiToBids, runPipeline, runQC, setupPipeline, addLowBToBIDS, qualityDistributions
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDialog, 
    QSizePolicy, QToolBar, QTextEdit, QStackedWidget, QComboBox, QSpinBox, QDialogButtonBox, QGraphicsScene
    )
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

# Dev Options:
VERSION = '''
0.1.0
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

class WarningPopUp(QDialog):
    def __init__(self, parent=None)->None:
        super().__init__(parent)
        self.setWindowTitle(f'WARNING')

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ignore | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        warningMessage = QLabel(f'It is NOT recommended to update your image files if analysis has been performed already.\nIf you proceed, the old image files will be renamed. not overwritten.')
        layout.addWidget(warningMessage)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    actionButtons:list[QPushButton] = []

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"DSI Studio Pipeline")
        self.Xstart = 150
        self.WIDTH = 1500
        self.Ystart = 100
        self.HEIGHT = 750
        self.setGeometry(self.Xstart, self.Ystart, self.WIDTH, self.HEIGHT)
    
        self.makeToolbar() # makes toolbar at top of screen
        self.centralStack = QStackedWidget()
        self.setCentralWidget(self.centralStack)
        self.centralStack.addWidget(self.MakeFunctionalWidget()) # makes central widget, status and buttons
        self.centralStack.addWidget(self.MakeVisualisationWidget())
        "#617977"
        for button in self.actionButtons:
            #button.clicked.connect(self.updateStatus)
            button.setProperty("class", 'functionalButton')

        self.setStyleSheet('''
                            QPushButton[class="functionalButton"]:disabled {
                                background: #617977;
                            }
                            QPushButton[class="functionalButton"]:hover {
                                background: #002E2E
                            }
                           ''')
    ### END __init__()

    def setupButtonClick(self)->None:
        warningResponse = WarningPopUp()
        if not warningResponse.exec():
            return

        self.label.setText("Attempting to set up directories...")
        self.makeButtonInactive(self.setupButton)
        self.setupAction() # determined when button is initialized
        self.label.setText("Setup complete!")
    
    def niftiButtonClick(self)->None:
        self.clearExecute()
        self.execButton.clicked.connect(self.niftiExecute)
        self.displayRegion.clear()
        self.displayRegion.append("SELECTED NIFTI TO BIDS\n")
        self.displayRegion.append("The following ID's will be converted to BIDS format:")
        source, ids, target = StatusChecker.niftiStatus()
        
        Debug.Log(StatusChecker.niftiStatus())
        for id in ids:
            self.displayRegion.append(id)
    def niftiExecute(self)->None:
        self.clearExecute()
        self.label.setText("Moving nifti files to BIDS format...")
        self.makeButtonInactive(self.niftiButton)
        restoreThese = self.timeOutButtons()
        proc = Process(target=niftiToBids.NiftiToBIDS)
        proc.start()
        self.label.setText("BIDS re-format complete!")
        self.restoreTimedOutButtons(restoreThese)

    def mriqcButtonClick(self)->None:
        self.clearExecute()
        self.execButton.clicked.connect(self.mriqcButtonExecute)
        self.displayRegion.clear()
        self.displayRegion.append("SELECTED MRIQC\n")
        self.displayRegion.append("The following ID's will be evaluated by MRIQC:")
        source, ids, target = StatusChecker.qcStatus()
        
        Debug.Log(StatusChecker.qcStatus())
        for id in ids:
            self.displayRegion.append(id)
    def mriqcButtonExecute(self)->None:
        self.clearExecute()
        self.label.setText("Running MRIQC...")
        self.makeButtonInactive(self.mriqcButton)
        restoreThese = self.timeOutButtons()
        proc = Process(target=runQC.RunMRIQC)
        proc.start()
        self.label.setText("MRIQC Complete!")
        self.restoreTimedOutButtons(restoreThese)

    def srcButtonClick(self)->None:
        self.clearExecute()
        self.execButton.clicked.connect(self.srcButtonExecute)
        self.displayRegion.clear()
        self.displayRegion.append("SELECTED SRC\n")
        self.displayRegion.append("The following ID's will go through Dsi Studio's SRC action:")
        source, ids, target = StatusChecker.srcStatus()
        
        Debug.Log(StatusChecker.srcStatus())
        for id in ids:
            self.displayRegion.append(id)
    def srcButtonExecute(self)->None:
        self.clearExecute()
        self.label.setText("Running SRC action")
        self.makeButtonInactive(self.srcButton)
        restoreThese = self.timeOutButtons()
        proc = Process(target=runPipeline.RunSRC)
        proc.start()
        self.label.setText("SRC Complete!")
        self.restoreTimedOutButtons(restoreThese)

    def recButtonClick(self)->None:
        self.clearExecute()
        self.execButton.clicked.connect(self.recButtonExecute)
        self.displayRegion.clear()
        self.displayRegion.append("SELECTED REC\n")
        self.displayRegion.append("The following ID's will go through Dsi Studio's REC action:")
        source, ids, target = StatusChecker.recStatus()

        Debug.Log(StatusChecker.recStatus())
        for id in ids:
            self.displayRegion.append(id)
    def recButtonExecute(self)->None:
        self.clearExecute()
        self.label.setText("Running REC action")
        self.makeButtonInactive(self.recButton)
        restoreThese = self.timeOutButtons()
        proc = Process(target=runPipeline.RunREC)
        proc.start()
        self.label.setText("REC Complete!")
        self.restoreTimedOutButtons(restoreThese)
    
    def clearExecute(self)->None:
        '''Disconnects Execute Button from any click signals, if connected.'''
        try:
            self.execButton.disconnect()
        except Exception as e:
            Debug.Log(f'{e}\n\tAttempet to disconnect execute button.', DEBUG)
    
    def refreshAll(self)->None:
        for b in self.actionButtons:
            b.setDisabled(False)
            b.setToolTip(None)
        self.clearExecute()
        self.label.setText('All buttons are reset.')
        self.displayRegion.clear()
        return

    def flipLowB(self)->None:
        result = addLowBToBIDS.FlipLOWBLocation()
        self.label.setText(result)
        return
    
    def toggleDisplay(self)->None:
        textOptions = ['Quality\nGraphs', 'Pipeline\nFunctions']
        newIndex = abs(self.centralStack.currentIndex() - 1)
        self.centralStack.setCurrentIndex(newIndex)
        self.visualiserButton.setText(textOptions[newIndex])
        return
    
    def timeOutButtons(self)->list:
        timedOut = []
        for button in self.actionButtons:
            if button.isEnabled():
                timedOut.append(button)
                button.setDisabled(True)
                button.setToolTip('Action in progress, please wait.')
        return timedOut
    
    def restoreTimedOutButtons(self, timedOut:list[QPushButton])->None:
        for button in timedOut:
            button.setDisabled(False)
            button.setToolTip(None)
    
    def updateStatus(self)->None:

        Debug.Log(f'Function not added', DEBUG)

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
        self.refreshButton.clicked.connect(self.refreshAll)
        self.refreshButton.setFixedSize(55, 45)

        self.flipLowBButton = QPushButton("Flip\nLow B")
        self.flipLowBButton.clicked.connect(self.flipLowB)
        self.flipLowBButton.setFixedSize(65, 45)

        self.visualiserButton = QPushButton("Quality\nGraphs")
        self.visualiserButton.clicked.connect(self.toggleDisplay)
        self.visualiserButton.setFixedSize(65, 45)

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
        toolbar.addWidget(self.visualiserButton)
        toolbar.addWidget(self.flipLowBButton)
        toolbar.addWidget(self.refreshButton)
        
        return
    
    def handleFigureTypeSelection(self, newType:str)->None:
        self.possibleFigures = self.figurePaths[newType]
        self.currFigureIndex = 0
        self.drawFigure(self.currFigureIndex)
        Debug.Log(f'{newType}')
        self.indexController.setMaximum(len(self.possibleFigures))
        pass

    def drawFigure(self, index:int)->None:
        Debug.Log(f"drawing... {index}", DEBUG)
        # if index >= len(self.possibleFigures):
        #     Debug.Log(f"Attempted index was out of range. Resetting to zero.")
        #     self.currFigureIndex = 0
        #     index = 0
        try:
            self.imagePixmap = QPixmap(self.possibleFigures[index])
            self.imageDisplayArea.setPixmap(self.imagePixmap)
        except Exception as e:
            Debug.Log(f'No images in Figures/ directory', DEBUG)
            self.imagePixmap = QPixmap()

    def MakeVisualisationWidget(self)->QWidget:
        visWidget = QWidget()
        layout = QHBoxLayout(visWidget)
        self.controlLabel = QLabel("Controls", self)
        self.controlLabel.setFont(QFont("Serif", 20))
        self.controlLabel.setStyleSheet(
            "color: #00FFDD;"
            "font-weight: bold;"
            )
        controls = QVBoxLayout()
        controls.addWidget(self.controlLabel)
        
        #T1Results, T2Results = qualityDistributions.RunAnatomical()
        #FuncResults = qualityDistributions.RunFunctional()
        t1Paths, t2Paths, dwiPaths = FetchFiles.FetchFigures()

        self.figurePaths = {
            'T1w': t1Paths, 
            'T2w': t2Paths, 
            'dwi': dwiPaths
            }
        self.typePullDown = QComboBox()
        for i, figType in enumerate(self.figurePaths.keys()):
            self.typePullDown.insertItem(i, figType)
        self.typePullDown.currentTextChanged.connect(self.handleFigureTypeSelection)
        self.possibleFigures = self.figurePaths[self.typePullDown.currentText()]
        self.currFigureIndex = 0
        self.drawFigure(self.currFigureIndex)

        controls.addWidget(self.typePullDown)

        self.indexController = QSpinBox() # initialized in handle type selection method
        self.indexController.setMinimum(0)
        self.indexController.setMaximum(len(self.possibleFigures))
        self.indexController.valueChanged.connect(self.drawFigure)
        controls.addWidget(self.indexController)

        self.imageDisplayArea = QLabel()
        self.imagePixmap = QPixmap(self.possibleFigures[0])
        self.imageDisplayArea.setPixmap(self.imagePixmap)

        controls.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.imageDisplayArea.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(controls, stretch=1)
        layout.addWidget(self.imageDisplayArea, stretch=4)
        return visWidget

    def MakeFunctionalWidget(self)->QWidget:
        centralWidgetFunctions = QWidget()
        #self.setCentralWidget(centralWidgetFunctions)
        layout = QHBoxLayout(centralWidgetFunctions) # main layout
        self.label = QLabel("Welcome!", self)
        self.label.setFont(QFont("Serif", 20))
        self.label.setStyleSheet(
            "color: #00FFDD;"
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
        self.actionButtons.append(self.setupButton)

        ### make nifti button
        self.niftiButton = QPushButton("Move nifti files to BIDS directory")
        self.niftiButton.clicked.connect(self.niftiButtonClick)
        self.niftiButton.setFixedSize(int(.6*self.WIDTH), int(.1*self.HEIGHT))
        vButtons.addWidget(self.niftiButton)
        self.actionButtons.append(self.niftiButton)

        ### make mriqc button
        self.mriqcButton = QPushButton("Run MRIQC for anatomical data")
        self.mriqcButton.clicked.connect(self.mriqcButtonClick)
        self.mriqcButton.setFixedSize(int(.6*self.WIDTH), int(.1*self.HEIGHT))
        vButtons.addWidget(self.mriqcButton)
        self.actionButtons.append(self.mriqcButton)

        ### make src button
        self.srcButton = QPushButton("Run DSI Studio src action for diffusion data")
        self.srcButton.clicked.connect(self.srcButtonClick)
        self.srcButton.setFixedSize(int(.6*self.WIDTH), int(.1*self.HEIGHT))
        vButtons.addWidget(self.srcButton)
        self.actionButtons.append(self.srcButton)

        ### make rec button
        self.recButton = QPushButton("Run DSI Studio rec action for diffusion data")
        self.recButton.clicked.connect(self.recButtonClick)
        self.recButton.setFixedSize(int(.6*self.WIDTH), int(.1*self.HEIGHT))
        vButtons.addWidget(self.recButton)
        self.actionButtons.append(self.recButton)

        ### make run button
        self.execButton = QPushButton("Execute Selected")
        #self.execButton.clicked.connect(self.updateStatus)
        self.execButton.setFixedSize(int(.25*self.width()), int(.125*self.height()))
        self.execButton.setObjectName("ExecButton")
        execButtonStyle = """
            #ExecButton {
                background-color: #1D5357;
                border: none;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
            }
            #ExecButton:hover {
                background-color: #3CA9B1;
            }
        """
        "#3CA9B1"
        self.execButton.setStyleSheet(execButtonStyle)
        vButtons.addWidget(self.execButton, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.displayRegion = QTextEdit()
        self.displayRegion.setReadOnly(True)

        layout.addLayout(vButtons, stretch=2)
        layout.addWidget(self.displayRegion, stretch=1)
        
        ### end buttons

        vButtons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #self.createMenuBar()
        self.statusBar().showMessage(f"Running DSI Studio Pipeline Interface App Version: {VERSION}")
        Debug.Log(len(self.findChildren(QPushButton)), DEBUG)
        return centralWidgetFunctions

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