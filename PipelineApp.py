import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"DSI Studio Pipeline")
        self.setGeometry(300, 200, 1100, 600) # x, y, w, h

        self.label = QLabel("Welcome3!", self)
        self.label.setFont(QFont("Arial", 30))
        self.label.setGeometry(0,0,200,50)
        self.label.setStyleSheet(
            "color: #361212;"
            "font-weight: bold;"
            )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()