import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

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
            "color: #361212;"
            "font-weight: bold;"
            )
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.label)

        self.setupButton = QPushButton("Set up directories")
        self.setupButton.clicked.connect(self.setupButtonClick)
        layout.addWidget(self.setupButton)
        if os.path.isdir('convertToBids'):
            # button will be inactive if setup does not need run again
            self.makeInactive(self.setupButton)

    def setupButtonClick(self):
        self.label.setText("Attempting to set up directories...")
        os.system(f'python setupPipeline.py')
        self.label.setText("Setup complete!")
        self.makeInactive(self.setupButton)

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