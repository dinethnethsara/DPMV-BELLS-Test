import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Import modules
from ui.splash_screen import SplashScreen
from ui.main_window import MainWindow

# Create application
app = QApplication(sys.argv)

# Create and show splash screen
splash = SplashScreen()
splash.show()

# Create and initialize main window
main_window = MainWindow()

# Function to close splash and show main window
def finish_splash():
    splash.close()
    main_window.show()

# Set timer to close splash after 3 seconds
QTimer.singleShot(3000, finish_splash)

# Execute app
sys.exit(app.exec_())