from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QColor, QPainter, QFont

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        
        # Create a custom pixmap for the splash screen
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.transparent)
        
        # Create a painter to draw on the pixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw glassmorphism effect
        painter.setBrush(QColor(20, 20, 30, 220))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 400, 300, 15, 15)
        
        # Draw logo/text
        painter.setPen(QColor(0, 200, 255))
        font = QFont("Arial", 24, QFont.Bold)
        painter.setFont(font)
        painter.drawText(0, 0, 400, 200, Qt.AlignCenter, "DPMMV")
        
        painter.setPen(QColor(220, 220, 255))
        font = QFont("Arial", 18)
        painter.setFont(font)
        painter.drawText(0, 30, 400, 200, Qt.AlignCenter, "Bells System")
        
        # Add loading text
        painter.setPen(QColor(150, 150, 220))
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.drawText(0, 190, 400, 50, Qt.AlignCenter, "Loading Bells...")
        
        # Draw a neon border glow
        painter.setPen(QColor(0, 180, 255, 100))
        painter.drawRoundedRect(2, 2, 396, 296, 15, 15)
        
        painter.end()
        
        # Set the pixmap to the splash screen
        self.setPixmap(pixmap)
        
        # Add a progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 240, 300, 20)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2d2d3a;
                border-radius: 5px;
                background-color: #1a1a2a;
                color: #ffffff;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                  stop:0 #00a0ff, stop:1 #00ffee);
                border-radius: 5px;
            }
        """)
        
        # Set up the progress animation
        self.counter = 0
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(30)
        
    def update_progress(self):
        """Update the progress bar animation"""
        self.counter += 1
        self.progress_bar.setValue(self.counter)
        
        if self.counter > 100:
            self.progress_timer.stop()