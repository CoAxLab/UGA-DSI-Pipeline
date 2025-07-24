import sys
import os
import Scripts
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

import Scripts.niftiToBids
import Scripts.setupPipeline

class MainWindow(QMainWindow):
    # class DSIButton(QPushButton):
    #     def __init__(self, action:function):
    #         super().__init__()
    #         self.action = action
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
            "color: #361212;"
            "font-weight: bold;"
            )
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.label)

        if os.path.isdir('convertToBids'):
            # only refresh images if directory setup already is complete
            self.setupButton = QPushButton("Pull Singularity images (create or update)")
            self.setupAction = Scripts.setupPipeline.UpdateImages
        else:
            self.setupButton = QPushButton("Set up directories")
            self.setupAction = Scripts.setupPipeline.main
        self.setupButton.clicked.connect(self.setupButtonClick)
        layout.addWidget(self.setupButton)

        self.niftiButton = QPushButton("Move nifti files to BIDS directory")
        self.niftiButton.clicked.connect(self.niftiButtonClick)
        layout.addWidget(self.niftiButton)

    def setupButtonClick(self):
        self.label.setText("Attempting to set up directories...")
        self.setupAction() # determined when button is initialized
        self.label.setText("Setup complete!")
        self.makeInactive(self.setupButton)
    
    def niftiButtonClick(self):
        self.label.setText("Moving nifti files to BIDS format...")
        Scripts.niftiToBids.NiftiToBIDS()
        self.label.setText("BIDS re-format complete!")
        self.makeInactive(self.niftiButton)

    def makeInactive(self, button:QPushButton):
        button.setDisabled(True)
        button.setToolTip("Action already complete!")

        


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()