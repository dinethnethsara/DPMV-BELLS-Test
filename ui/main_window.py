from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
    QListWidget, QListWidgetItem, QFrame, QSplitter, QScrollArea, QTabWidget,
    QTimeEdit, QLineEdit, QComboBox, QSlider, QGroupBox, QSpinBox, QMenuBar,
    QMenu, QAction, QSystemTrayIcon, QMessageBox, QSizePolicy, QFileDialog,
    QToolButton, QGridLayout
)
from PyQt5.QtCore import Qt, QTime, QTimer, QSize, QDateTime, QDate
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPixmap
import json
import os
import sys

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Set up layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title
        self.title = QLabel("DPMMV Bells System")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 14px; font-weight: bold; color: #00a0ff;")
        
        # Add buttons
        self.minimize_btn = QPushButton("—")
        self.minimize_btn.setFixedSize(30, 25)
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(30, 25)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 25)
        self.close_btn.clicked.connect(self.parent.close)
        
        # Add to layout
        self.layout.addSpacing(5)
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.minimize_btn)
        self.layout.addWidget(self.maximize_btn)
        self.layout.addWidget(self.close_btn)
        
        # Style the widgets
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #cccccc;
            }
            QPushButton:hover {
                background-color: #353546;
            }
            #close_btn:hover {
                background-color: #ff0000;
                color: white;
            }
        """)
        self.close_btn.setObjectName("close_btn")
        
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.move(event.globalPos() - self.parent.drag_position)
            event.accept()

class NextBellWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
            border: 1px solid #353550;
        """)
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        
        # Add header
        self.header = QLabel("Next Bell")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a0ff;")
        
        # Add bell name
        self.bell_name = QLabel("Period 1")
        self.bell_name.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        
        # Add countdown
        self.countdown = QLabel("00:15:22")
        self.countdown.setStyleSheet("font-size: 36px; font-weight: bold; color: #00ffee;")
        
        # Add time
        self.time = QLabel("10:30 AM")
        self.time.setStyleSheet("font-size: 18px; color: #8080a0;")
        
        # Add to layout
        self.layout.addWidget(self.header, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.bell_name, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.countdown, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.time, alignment=Qt.AlignCenter)

class BellListWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
            border: 1px solid #353550;
        """)
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        
        # Add header with controls
        self.header_layout = QHBoxLayout()
        self.title = QLabel("Today's Bells")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a0ff;")
        
        self.add_btn = QPushButton("+ Add Bell")
        self.add_btn.setStyleSheet("""
            background-color: #00a0ff;
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
        """)
        
        self.filter_btn = QPushButton("🔍 Filter")
        self.filter_btn.setStyleSheet("""
            background-color: #2d2d40;
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
        """)
        
        self.header_layout.addWidget(self.title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.filter_btn)
        self.header_layout.addWidget(self.add_btn)
        
        # Add bell list
        self.bell_list = QListWidget()
        self.bell_list.setStyleSheet("""
            QListWidget {
                background-color: #252535;
                border-radius: 5px;
                border: 1px solid #353550;
                padding: 5px;
            }
            QListWidget::item {
                border-bottom: 1px solid #353550;
                padding: 5px;
                margin-bottom: 5px;
            }
            QListWidget::item:selected {
                background-color: #404060;
            }
        """)
        
        # Add sample bells
        for i, (time, name) in enumerate([
            ("09:00 AM", "School Start"),
            ("10:30 AM", "Period 1"),
            ("11:20 AM", "Break"),
            ("11:35 AM", "Period 2"),
            ("12:25 PM", "Lunch"),
            ("13:10 PM", "Period 3"),
            ("14:00 PM", "End of Day")
        ]):
            item = QListWidgetItem(f"{time} - {name}")
            self.bell_list.addItem(item)
        
        # Add to layout
        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.bell_list)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        
        # Set window properties
        self.setWindowTitle("DPMMV Bells System")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(900, 600)
        
        # Set up dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121220;
                color: white;
            }
            QWidget {
                background-color: #121220;
                color: white;
            }
            QPushButton {
                background-color: #2d2d40;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #3d3d50;
            }
            QTabWidget::pane {
                background-color: #1a1a2a;
                border: 1px solid #353550;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #252535;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #353550;
            }
        """)
        
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add custom title bar
        self.title_bar = CustomTitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # Add a separator line
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.separator.setStyleSheet("background-color: #353550; max-height: 1px;")
        self.main_layout.addWidget(self.separator)
        
        # Create content widget with margins
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        
        # Add current time and date
        self.header_layout = QHBoxLayout()
        
        self.current_time = QLabel("10:30:15 AM")
        self.current_time.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        
        self.current_date = QLabel("Monday, May 10, 2025")
        self.current_date.setStyleSheet("font-size: 16px; color: #8080a0;")
        
        self.status_label = QLabel("All Bells Active")
        self.status_label.setStyleSheet("""
            background-color: #00a05030;
            color: #00ffee;
            padding: 5px 10px;
            border-radius: 10px;
            font-weight: bold;
        """)
        
        self.header_layout.addWidget(self.current_time)
        self.header_layout.addWidget(self.current_date)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.status_label)
        
        self.content_layout.addLayout(self.header_layout)
        
        # Create dashboard layout
        self.dashboard_layout = QHBoxLayout()
        
        # Add next bell widget (left side)
        self.next_bell_widget = NextBellWidget()
        self.next_bell_widget.setFixedWidth(250)
        
        # Add bell list (right side)
        self.bell_list_widget = BellListWidget()
        
        # Add to dashboard layout
        self.dashboard_layout.addWidget(self.next_bell_widget)
        self.dashboard_layout.addWidget(self.bell_list_widget)
        
        # Add dashboard to content
        self.content_layout.addLayout(self.dashboard_layout)
        
        # Add tabs for more features
        self.tabs = QTabWidget()
        
        # Timeline tab
        self.timeline_tab = QWidget()
        self.tabs.addTab(self.timeline_tab, "Timeline")
        
        # Analytics tab
        self.analytics_tab = QWidget()
        self.tabs.addTab(self.analytics_tab, "Analytics")
        
        # Settings tab
        self.settings_tab = QWidget()
        self.tabs.addTab(self.settings_tab, "Settings")
        
        # Tools tab
        self.tools_tab = QWidget()
        self.tabs.addTab(self.tools_tab, "Tools")
        
        # Add tabs to content
        self.content_layout.addWidget(self.tabs)
        
        # Add content widget to main layout
        self.main_layout.addWidget(self.content_widget)
        
        # Set up status bar
        self.status_bar = QFrame()
        self.status_bar.setStyleSheet("""
            background-color: #252535;
            max-height: 25px;
            border-top: 1px solid #353550;
        """)
        self.status_bar_layout = QHBoxLayout(self.status_bar)
        self.status_bar_layout.setContentsMargins(10, 0, 10, 0)
        
        self.status_text = QLabel("Ready - Next bell in 15:22")
        self.status_version = QLabel("v1.0.0")
        
        self.status_bar_layout.addWidget(self.status_text)
        self.status_bar_layout.addStretch()
        self.status_bar_layout.addWidget(self.status_version)
        
        self.main_layout.addWidget(self.status_bar)
        
        # Create system tray icon
        self.setup_tray_icon()
        
        # Set up timers for date and time
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        
        # Update time at start
        self.update_time()
        
    def setup_tray_icon(self):
        """Set up system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        # Use a dummy icon for now
        self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        
        # Create tray menu
        self.tray_menu = QMenu()
        
        # Add menu actions
        self.show_action = QAction("Show", self)
        self.show_action.triggered.connect(self.show)
        
        self.hide_action = QAction("Hide", self)
        self.hide_action.triggered.connect(self.hide)
        
        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.close_application)
        
        # Add actions to menu
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.hide_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.exit_action)
        
        # Set tray menu
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Show tray icon
        self.tray_icon.show()
        
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_visibility()
            
    def toggle_visibility(self):
        """Toggle window visibility"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
            
    def close_application(self):
        """Close the application completely"""
        self.tray_icon.hide()
        QApplication.quit()
        
    def closeEvent(self, event):
        """Handle close event to minimize to tray instead of closing"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "DPMMV Bells System",
            "Application minimized to tray. Bells will continue to play.",
            QSystemTrayIcon.Information,
            2000
        )
        
    def update_time(self):
        """Update the current time and date display"""
        now = QDateTime.currentDateTime()
        self.current_time.setText(now.toString("hh:mm:ss AP"))
        self.current_date.setText(now.toString("dddd, MMMM d, yyyy"))