import sys, os, argparse
from collections import defaultdict
## from multiprocessing import Process
from Scripts.Util import Debug, StatusChecker, FetchFiles
from Scripts.ProcessingScripts import niftiToBids, runPipeline,  setupPipeline, addLowBToBIDS
from Scripts.AnalysisScripts import runQC
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QDialog, 
    QSizePolicy, QToolBar, QTextEdit, QTextBrowser, QStackedWidget, QComboBox, QDialogButtonBox, QFileDialog
    )
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from Scripts.ProcessingScripts.DoMigration import CheckAndMigrate

# Dev Options:
VERSION = '''
1.0.0
'''
pipelineDirectory = os.getcwd()
# End Dev Options

class DSIFunctionalButton(QPushButton):
    """Custom QPushButton to eliminate boilerplate in MainWindow."""
    def __init__(self, text: str, callback: callable, window_width: int, window_height: int):
        super().__init__(text)
        self.clicked.connect(callback)
        self.setFixedSize(int(0.6 * window_width), int(0.1 * window_height))

class InputDirChangePopUp(QDialog):
    def __init__(self, parent=None)->None:
        super().__init__(parent)
        self.setWindowTitle(f'Change Input Location')

        self.buttons= QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.No)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel(f'Select OK if you wish to select an input directory separate from the pipeline default')
        layout.addWidget(message)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

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

class DSIStudioConfirm(QDialog):
    def __init__(self, parent=None)->None:
        super().__init__(parent)
        self.setWindowTitle(f'External Program Confirmation')

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Open | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        warningMessage = QLabel(f'You are about to launch DSI Studio fiber tracking.')
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

    def GetNewDirectoryPath(self)->str:
        directory = QFileDialog.getExistingDirectory(self,
                                                     'Select Directory',
                                                     pipelineDirectory,
                                                     QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        return directory if (directory) else None

    ### START Main window buttons
    def setupButtonClick(self)->None:
        warningResponse = WarningPopUp()
        if not warningResponse.exec():
            return

        self.label.setText("Attempting to set up directories...")
        self.makeButtonInactive(self.setupButton)
        CheckAndMigrate()
        self.setupAction() # determined when button is initialized
        self.label.setText("Setup complete!")
    
    def niftiButtonClick(self)->None:
        self.clearExecute()
        selectInputResponse = InputDirChangePopUp()
        if selectInputResponse.exec():
            self.niftiDirectory = self.GetNewDirectoryPath()
        else:
            self.niftiDirectory = None
        self.execButton.clicked.connect(self.niftiExecute)
        self.displayRegion.clear()
        self.displayRegion.append("SELECTED NIFTI TO BIDS\n")
        self.displayRegion.append("The following ID's will be converted to BIDS format:")
        source, ids, target = StatusChecker.niftiStatus(self.niftiDirectory)
        
        Debug.Log(f'{source}, {ids} {target}', DEBUG)
        for id in ids:
            self.displayRegion.append(id)
    def niftiExecute(self)->None:
        self.label.setText("Moving nifti files to BIDS format...")
        self.makeButtonInactive(self.niftiButton)
        restoreThese = self.timeOutButtons()
        # proc = Process(target=niftiToBids.NiftiToBIDS)
        # proc.start()
        # proc.join()
        niftiToBids.NiftiToBIDS(self.niftiDirectory)
        self.label.setText("BIDS re-format complete!")
        self.restoreTimedOutButtons(restoreThese)
        self.clearExecute()

    def mriqcButtonClick(self)->None:
        self.clearExecute()
        self.execButton.clicked.connect(self.mriqcButtonExecute)
        self.displayRegion.clear()
        self.displayRegion.append("SELECTED MRIQC\n")
        self.displayRegion.append("The following ID's will be evaluated by MRIQC:")
        source, ids, target = StatusChecker.qcStatus()
        
        Debug.Log(f'{source}, {ids} {target}', DEBUG)
        for id in ids:
            self.displayRegion.append(id)
    def mriqcButtonExecute(self)->None:
        self.label.setText("Running MRIQC...")
        self.makeButtonInactive(self.mriqcButton)
        restoreThese = self.timeOutButtons()
        # proc = Process(target=runQC.RunMRIQC)
        # proc.start()
        # proc.join()
        runQC.RunMRIQC()
        self.label.setText("MRIQC Complete!")
        self.restoreTimedOutButtons(restoreThese)
        self.clearExecute()

    def srcButtonClick(self)->None:
        self.clearExecute()
        self.execButton.clicked.connect(self.srcButtonExecute)
        self.displayRegion.clear()
        self.displayRegion.append("SELECTED SRC\n")
        self.displayRegion.append("The following ID's will go through Dsi Studio's SRC action:")
        source, ids, target = StatusChecker.srcStatus()
        
        Debug.Log(f'{source}, {ids} {target}', DEBUG)
        for id in ids:
            self.displayRegion.append(id)
    def srcButtonExecute(self)->None:
        self.label.setText("Running SRC action")
        self.makeButtonInactive(self.srcButton)
        restoreThese = self.timeOutButtons()
        # proc = Process(target=runPipeline.RunSRC)
        # proc.start()
        # proc.join()
        runPipeline.RunSRC()
        self.label.setText("SRC Complete!")
        self.restoreTimedOutButtons(restoreThese)
        self.clearExecute()

    def recButtonClick(self)->None:
        self.clearExecute()
        self.execButton.clicked.connect(self.recButtonExecute)
        self.displayRegion.clear()
        self.displayRegion.append("SELECTED REC\n")
        self.displayRegion.append("The following ID's will go through Dsi Studio's REC action:")
        source, ids, target = StatusChecker.recStatus()

        Debug.Log(f'{source}, {ids} {target}', DEBUG)
        for id in ids:
            self.displayRegion.append(id)
    def recButtonExecute(self)->None:
        self.label.setText("Running REC action")
        self.makeButtonInactive(self.recButton)
        restoreThese = self.timeOutButtons()
        # proc = Process(target=runPipeline.RunREC)
        # proc.start()
        # proc.join()
        runPipeline.RunREC()
        self.label.setText("REC Complete!")
        self.restoreTimedOutButtons(restoreThese)
        self.clearExecute()
    ### END Main buttons
    
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
    
    def tryExport(self)->None:
        self.label.setText('Attempting to run DSI Studio qa export...')
        runPipeline.RunQAExport()
        self.label.setText('DSI Studio qa export is complete. Check Output/fib/ for desired data.')
    
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
        self.refreshButton.setFixedSize(70, 45)

        self.flipLowBButton = QPushButton("Flip\nLow B")
        self.flipLowBButton.clicked.connect(self.flipLowB)
        self.flipLowBButton.setFixedSize(80, 45)

        self.exportButton = QPushButton('Export\nQA')
        self.exportButton.clicked.connect(self.tryExport)
        self.exportButton.setFixedSize(80, 45)

        self.visualiserButton = QPushButton("Quality\nGraphs")
        self.visualiserButton.clicked.connect(self.toggleDisplay)
        self.visualiserButton.setFixedSize(80, 45)

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
        toolbar.addWidget(self.exportButton)
        toolbar.addWidget(self.refreshButton)
        
        return
    
    def handleFigureTypeSelection(self, newType:str)->None:
        self.possibleFigures = self.figurePaths[newType]
        self.currFigureIndex = 0
        #self.drawFigure(self.currFigureIndex)
        Debug.Log(f'{newType}', DEBUG)
        self.fillMeasurePullDown()
        #self.indexController.setMaximum(len(self.possibleFigures))
        pass

    def drawFigure(self, index:int)->None:
        if index == -1: return
        Debug.Log(f"drawing... {index}", DEBUG)
        if index >= len(self.possibleFigures):
            Debug.Log(f"Attempted index was out of range. Resetting to zero.", DEBUG)
            self.currFigureIndex = 0
            index = 0
        currType = self.typePullDown.currentText()
        currMeasure = self.measurePullDown.currentText().lower()
        currMeasure = currMeasure.replace('r2', 'R2')
        currMeasure = currMeasure.replace('t1w_', '')
        currMeasure = currMeasure.replace('t2w_', '')
        Debug.Log(f'Curr measure is: {currMeasure}', DEBUG)
        try:
            self.imagePixmap = QPixmap(self.possibleFigures[index])
            self.imageDisplayArea.setPixmap(self.imagePixmap)
            self.textStatusRegion.clear()
            #Debug.Log(f'current type: {currType}, current measure: {currMeasure})', DEBUG)
            outlierList, outlierValuesList = self.OutlierIDDict[currType][currMeasure]
            #Debug.Log(f'Outlier List and Values: {outlierList}\n{outlierValuesList}', DEBUG)
            htmlContent = """
            <h3 style='color: #FBECFD; margin-bottom: 10px; border-bottom: 1px solid #444;'>
                Flagged Outliers
            </h3>
            """
            if outlierList == []:
                htmlContent += "<p style='color: #50FA7B;'>No outliers detected.</p>"
                Debug.Log(f'Not Creating HTML Entries: No Outliers', DEBUG)
            else:
                grouped = defaultdict(list)
                for i, item in enumerate(outlierList):
                    # Split 'sub-x_ses-n' for better visual hierarchy
                    tokens = item.split('_')
                    sub_id = tokens[0].replace('sub-', '')
                    ses_id = tokens[1].replace('ses-', '')
                    value = outlierValuesList[i]
                    payload = f'action://sub-{sub_id}_ses-{ses_id}'
                    displayText = f'{ses_id} ({round(value, 5)})'
                    linkHTML = f"<a href='{payload}' style='color: #FF5555; text-decoration: none;'>{displayText}</a>"
                    grouped[sub_id].append(linkHTML)
                    Debug.Log(f'Created Hyperlink', DEBUG)
                
                Debug.Log(f'grouped dict: {grouped}', DEBUG)
                for sub_id in sorted(grouped.keys()):
                    sessions = ",<br>".join(sorted(grouped[sub_id]))
                    htmlContent += f"""
                    <div style='margin-bottom: 12px;'>
                        <span style='color: #FF5555; font-weight: bold;'>[!]</span> 
                        <span style='color: #FBECFD;'>Subject:</span> {sub_id}<br>
                        <span style='margin-left: 22px; color: #888;'>Sessions: <br>{sessions}</span>
                    </div>
                    """
                    Debug.Log(f'Created HTML Entry', DEBUG)
            self.textStatusRegion.setHtml(htmlContent)
            
        except Exception as e:
            Debug.Log(f'No images in Figures/ directory\n{e}\n', DEBUG)
            self.imagePixmap = QPixmap()
    
    def handleLinkClick(self, url)->None: # url is of type QUrl

        dsiConfirmation = DSIStudioConfirm()
        if not dsiConfirmation.exec():
            return
        subSes = url.toString()
        if subSes.startswith('action://'):
            subSes = subSes.replace('action://', '')
        FetchFiles.OpenFibFile(subSes)

    def fillMeasurePullDown(self)->None:
        self.measurePullDown.clear()
        for i, path in enumerate(self.possibleFigures):
            tokens = os.path.basename(path).split('_distribution')
            currMeasure = tokens[0]
            if 'dwi_' in currMeasure:
                currMeasure = currMeasure.replace('dwi_', '')
            measureLabel = currMeasure.upper()
            self.measurePullDown.insertItem(i, measureLabel)

    def MakeVisualisationWidget(self)->QWidget:
        visWidget = QWidget()
        layout = QHBoxLayout(visWidget)
        self.controlLabel = QLabel("Controls", self)
        self.controlLabel.setFont(QFont("Serif", 20))
        self.controlLabel.setStyleSheet(
            "color: #00695B;"
            "font-weight: bold;"
            )
        controls = QVBoxLayout()
        controls.addWidget(self.controlLabel)
        
        t1Paths, t2Paths, dwiPaths = FetchFiles.FetchFigures()

        
        ## Get metadata for figures to identify outlier IDs
        t1FigMetaData, t2FigMetaData, dwiFigmetaData = FetchFiles.FetchDFs()

        ## Each subdict has a Measures (str) as keys, mapped to outlierID and outlierValue (tuple)
        self.OutlierIDDict = {
            'T1w': {},
            'T2w': {},
            'dwi': {}
        }

        for t, df in enumerate([t1FigMetaData, t2FigMetaData, dwiFigmetaData]):
            scanTypes = ['T1w', 'T2w', 'dwi']
            currType = scanTypes[t]
            for col in df:
                Debug.Log(f'Outliers for measure: {currType},{col}', DEBUG)
                if 'source' in col or 'Outlier' in col or ' ' in col: continue
                currOutliers = df.loc[df[f'{col}_Outliers'] == 1, 'source_id'].tolist()
                currValues = df.loc[df[f'{col}_Outliers'] == 1, col].tolist()
                Debug.Log(f'Adding to Outlier Dict: {currOutliers},{currValues}', DEBUG)
                self.OutlierIDDict[currType][col] = (currOutliers, currValues)
        Debug.Log(f'Outlier Dict:\n{self.OutlierIDDict}\n', DEBUG)

        self.figurePaths = {
            'T1w': t1Paths, 
            'T2w': t2Paths, 
            'dwi': dwiPaths
            }
        self.typePullDown = QComboBox()
        
        for i, figType in enumerate(self.figurePaths.keys()):
            self.typePullDown.insertItem(i, figType)
        self.typePullDown.currentTextChanged.connect(self.handleFigureTypeSelection)
        self.measurePullDown = QComboBox()
        self.measurePullDown.currentIndexChanged.connect(self.drawFigure)

        controls.addWidget(self.typePullDown)
        controls.addWidget(self.measurePullDown)

        self.imageDisplayArea = QLabel()
        controls.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.imageDisplayArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textStatusRegion = QTextBrowser()
        self.textStatusRegion.setOpenExternalLinks(False)
        self.textStatusRegion.setReadOnly(True)
        self.textStatusRegion.anchorClicked.connect(self.handleLinkClick)
        self.textStatusRegion.setStyleSheet("""
                                                QTextEdit {
                                                    background-color: #1A1A1B;
                                                    color: #E0E0E0;
                                                    border: 2px solid #303033;
                                                    border-radius: 5px;
                                                    padding: 8px;
                                                    font-family: 'Consolas', 'Monaco', monospace;
                                                    font-size: 11pt;
                                                }
                                            """)

        self.handleFigureTypeSelection(self.typePullDown.currentText()) ## Fills measure pulldown and draws figure

        layout.addLayout(controls, stretch=1)
        layout.addWidget(self.imageDisplayArea, stretch=4)
        layout.addWidget(self.textStatusRegion, stretch=1)
        return visWidget

    def MakeFunctionalWidget(self)->QWidget:
        centralWidgetFunctions = QWidget()
        #self.setCentralWidget(centralWidgetFunctions)
        layout = QHBoxLayout(centralWidgetFunctions) # main layout
        self.label = QLabel("Welcome!", self)
        self.label.setFont(QFont("Serif", 20))
        self.label.setStyleSheet(
            "color: #00695B;"
            "font-weight: bold;"
            )

        # making vertical buttons widget
        vButtons = QVBoxLayout()
        vButtons.addWidget(self.label)

        ### make setup button

        def addActionButton(text: str, callback: callable) -> DSIFunctionalButton:
            btn = DSIFunctionalButton(text, callback, self.WIDTH, self.HEIGHT)
            vButtons.addWidget(btn)
            self.actionButtons.append(btn)
            return btn

        setupDirsExist = StatusChecker.SetupDirsStatus()
        if setupDirsExist:
            Debug.Log(f'Setup not needed.', DEBUG)
        else:
            Debug.Log(f'Directories have not yet been set up. Doing that now...', DEBUG)
            self.setupButton = addActionButton("Set up directories", self.setupButtonClick)
            self.setupAction = setupPipeline.main

        self.niftiButton = addActionButton("Move nifti files to BIDS directory", self.niftiButtonClick)

        self.mriqcButton = addActionButton("Run MRIQC for anatomical data", self.mriqcButtonClick)
        
        self.srcButton = addActionButton("Run DSI Studio src action for diffusion data", self.srcButtonClick)
        
        self.recButton = addActionButton("Run DSI Studio rec action for diffusion data", self.recButtonClick)

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
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', help='flag to print out debugging statements to terminal')
    args = parser.parse_args()
    global DEBUG
    DEBUG = args.debug

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()