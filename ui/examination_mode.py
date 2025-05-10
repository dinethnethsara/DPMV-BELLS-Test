from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QDialog, QSpinBox, QTimeEdit, QDateEdit, QCheckBox, QComboBox,
    QFormLayout, QLineEdit, QMessageBox, QSizePolicy, QSlider
)
from PyQt5.QtCore import Qt, QTime, QTimer, QDateTime, pyqtSignal
from PyQt5.QtGui import QFont, QColor

import time
import os

class ExamTimerWidget(QFrame):
    """Widget displaying a countdown timer for exams"""
    
    # Signal emitted when timer is complete
    timer_complete = pyqtSignal(str)  # timer_id
    
    def __init__(self, timer_id="exam", name="Exam", duration=60, parent=None):
        super().__init__(parent)
        self.timer_id = timer_id
        self.name = name
        self.total_seconds = duration * 60  # Convert minutes to seconds
        self.seconds_left = self.total_seconds
        self.running = False
        self.warning_threshold = 0.25  # Start warning color at 25% time left
        self.urgent_threshold = 0.1   # Start urgent color at 10% time left
        
        # Set up UI
        self.setup_ui()
        
        # Create timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.setInterval(1000)  # 1 second
        
    def setup_ui(self):
        """Set up the widget UI"""
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
            border: 1px solid #353550;
            padding: 5px;
        """)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Timer name
        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #00a0ff;
        """)
        
        # Timer display
        self.timer_display = QLabel(self.format_time(self.seconds_left))
        self.timer_display.setAlignment(Qt.AlignCenter)
        self.timer_display.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: white;
            font-family: monospace;
        """)
        
        # Progress bar
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet("""
            background-color: #00a0ff;
            border-radius: 5px;
        """)
        
        self.progress_bg = QFrame()
        self.progress_bg.setFixedHeight(10)
        self.progress_bg.setStyleSheet("""
            background-color: #2d2d40;
            border-radius: 5px;
        """)
        
        # Progress bar layout
        self.progress_layout = QHBoxLayout()
        self.progress_layout.setContentsMargins(0, 0, 0, 0)
        self.progress_layout.setSpacing(0)
        self.progress_layout.addWidget(self.progress_bar)
        
        self.progress_bg.setLayout(self.progress_layout)
        
        # Control buttons
        self.button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        self.start_button.setStyleSheet("""
            background-color: #00ff99;
            color: black;
            border-radius: 5px;
            padding: 5px 10px;
            font-weight: bold;
        """)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_timer)
        self.pause_button.setEnabled(False)
        self.pause_button.setStyleSheet("""
            background-color: #ffaa00;
            color: black;
            border-radius: 5px;
            padding: 5px 10px;
            font-weight: bold;
        """)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)
        self.reset_button.setEnabled(False)
        self.reset_button.setStyleSheet("""
            background-color: #ff5500;
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
            font-weight: bold;
        """)
        
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.pause_button)
        self.button_layout.addWidget(self.reset_button)
        
        # Add all elements to main layout
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.timer_display)
        self.layout.addWidget(self.progress_bg)
        self.layout.addLayout(self.button_layout)
        
        # Update progress bar
        self.update_progress_bar()
        
    def format_time(self, seconds):
        """Format seconds into HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
            
    def update_timer(self):
        """Update the timer display"""
        if self.seconds_left > 0:
            self.seconds_left -= 1
            self.timer_display.setText(self.format_time(self.seconds_left))
            self.update_progress_bar()
        else:
            self.timer.stop()
            self.running = False
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.reset_button.setEnabled(True)
            self.timer_complete.emit(self.timer_id)
            
    def update_progress_bar(self):
        """Update the progress bar width and color"""
        if self.total_seconds > 0:
            progress = self.seconds_left / self.total_seconds
        else:
            progress = 0
            
        # Update progress bar width
        width = int(self.progress_bg.width() * progress)
        self.progress_bar.setFixedWidth(width)
        
        # Update color based on time left
        if progress <= self.urgent_threshold:
            self.progress_bar.setStyleSheet("""
                background-color: #ff0000;
                border-radius: 5px;
            """)
            # Make timer display flash
            if self.seconds_left % 2 == 0:
                self.timer_display.setStyleSheet("""
                    font-size: 48px;
                    font-weight: bold;
                    color: #ff0000;
                    font-family: monospace;
                """)
            else:
                self.timer_display.setStyleSheet("""
                    font-size: 48px;
                    font-weight: bold;
                    color: white;
                    font-family: monospace;
                """)
        elif progress <= self.warning_threshold:
            self.progress_bar.setStyleSheet("""
                background-color: #ffaa00;
                border-radius: 5px;
            """)
            self.timer_display.setStyleSheet("""
                font-size: 48px;
                font-weight: bold;
                color: #ffaa00;
                font-family: monospace;
            """)
        else:
            self.progress_bar.setStyleSheet("""
                background-color: #00a0ff;
                border-radius: 5px;
            """)
            self.timer_display.setStyleSheet("""
                font-size: 48px;
                font-weight: bold;
                color: white;
                font-family: monospace;
            """)
            
    def resizeEvent(self, event):
        """Handle resize events to update progress bar"""
        super().resizeEvent(event)
        self.update_progress_bar()
        
    def start_timer(self):
        """Start or resume the timer"""
        if self.seconds_left == 0:
            self.reset_timer()
            
        self.running = True
        self.timer.start()
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        
    def pause_timer(self):
        """Pause the timer"""
        self.running = False
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        
    def reset_timer(self):
        """Reset the timer"""
        self.timer.stop()
        self.seconds_left = self.total_seconds
        self.timer_display.setText(self.format_time(self.seconds_left))
        self.running = False
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.update_progress_bar()
        
    def set_duration(self, minutes):
        """Set a new duration for the timer"""
        self.total_seconds = minutes * 60
        
        # If not running, reset the timer
        if not self.running:
            self.seconds_left = self.total_seconds
            self.timer_display.setText(self.format_time(self.seconds_left))
            self.update_progress_bar()
            
    def set_name(self, name):
        """Set a new name for the timer"""
        self.name = name
        self.name_label.setText(name)


class ExamConfigDialog(QDialog):
    """Dialog for configuring an exam session"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configure Examination Mode")
        self.setMinimumSize(450, 400)
        
        # Set up the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI"""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Form layout for exam settings
        self.form_layout = QFormLayout()
        
        # Exam name
        self.name_edit = QLineEdit("Final Examination")
        self.form_layout.addRow("Exam Name:", self.name_edit)
        
        # Exam date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDateTime.currentDateTime().date())
        self.date_edit.setCalendarPopup(True)
        self.form_layout.addRow("Exam Date:", self.date_edit)
        
        # Exam duration
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 240)  # 1 minute to 4 hours
        self.duration_spin.setValue(60)  # Default 1 hour
        self.duration_spin.setSuffix(" minutes")
        self.form_layout.addRow("Exam Duration:", self.duration_spin)
        
        # Reading time
        self.reading_time_layout = QHBoxLayout()
        
        self.reading_time_check = QCheckBox("Include reading time")
        self.reading_time_check.setChecked(True)
        self.reading_time_check.stateChanged.connect(self.toggle_reading_time)
        
        self.reading_time_spin = QSpinBox()
        self.reading_time_spin.setRange(1, 60)
        self.reading_time_spin.setValue(10)  # Default 10 minutes
        self.reading_time_spin.setSuffix(" minutes")
        
        self.reading_time_layout.addWidget(self.reading_time_check)
        self.reading_time_layout.addWidget(self.reading_time_spin)
        
        self.form_layout.addRow("Reading Time:", self.reading_time_layout)
        
        # Warning bells
        self.warning_layout = QHBoxLayout()
        
        self.warning_check = QCheckBox("Play warning bell")
        self.warning_check.setChecked(True)
        self.warning_check.stateChanged.connect(self.toggle_warning_time)
        
        self.warning_spin = QSpinBox()
        self.warning_spin.setRange(1, 60)
        self.warning_spin.setValue(5)  # Default 5 minutes
        self.warning_spin.setSuffix(" minutes before end")
        
        self.warning_layout.addWidget(self.warning_check)
        self.warning_layout.addWidget(self.warning_spin)
        
        self.form_layout.addRow("Warning Bell:", self.warning_layout)
        
        # Bell sound
        self.bell_sound_combo = QComboBox()
        self.bell_sound_combo.addItems(["Default Bell", "Exam Bell", "Soft Bell", "Electronic Tone"])
        self.form_layout.addRow("Bell Sound:", self.bell_sound_combo)
        
        # Display mode
        self.display_mode_combo = QComboBox()
        self.display_mode_combo.addItems(["Windowed", "Full Screen", "Full Screen with Controls"])
        self.form_layout.addRow("Display Mode:", self.display_mode_combo)
        
        # Add the form layout to the main layout
        self.layout.addLayout(self.form_layout)
        
        # Additional options
        self.options_group = QWidget()
        self.options_layout = QVBoxLayout(self.options_group)
        
        self.show_clock_check = QCheckBox("Show current time")
        self.show_clock_check.setChecked(True)
        
        self.auto_start_check = QCheckBox("Start exam mode automatically")
        self.auto_start_check.setChecked(False)
        
        self.play_start_check = QCheckBox("Play bell at start of exam")
        self.play_start_check.setChecked(True)
        
        self.play_end_check = QCheckBox("Play bell at end of exam")
        self.play_end_check.setChecked(True)
        
        self.options_layout.addWidget(self.show_clock_check)
        self.options_layout.addWidget(self.auto_start_check)
        self.options_layout.addWidget(self.play_start_check)
        self.options_layout.addWidget(self.play_end_check)
        
        self.layout.addWidget(self.options_group)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.start_button = QPushButton("Start Exam Mode")
        self.start_button.clicked.connect(self.accept)
        self.start_button.setStyleSheet("""
            background-color: #00a0ff;
            color: white;
            font-weight: bold;
            padding: 8px 16px;
        """)
        
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.start_button)
        
        self.layout.addLayout(self.button_layout)
        
    def toggle_reading_time(self, state):
        """Enable or disable reading time spinner"""
        self.reading_time_spin.setEnabled(state)
        
    def toggle_warning_time(self, state):
        """Enable or disable warning time spinner"""
        self.warning_spin.setEnabled(state)
        
    def get_config(self):
        """Get the exam configuration"""
        config = {
            "name": self.name_edit.text(),
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "duration": self.duration_spin.value(),
            "reading_time": self.reading_time_spin.value() if self.reading_time_check.isChecked() else 0,
            "warning_bell": self.warning_spin.value() if self.warning_check.isChecked() else 0,
            "bell_sound": self.bell_sound_combo.currentText(),
            "display_mode": self.display_mode_combo.currentText(),
            "show_clock": self.show_clock_check.isChecked(),
            "auto_start": self.auto_start_check.isChecked(),
            "play_start_bell": self.play_start_check.isChecked(),
            "play_end_bell": self.play_end_check.isChecked(),
        }
        return config


class ExaminationModeWidget(QWidget):
    """Widget for running examination mode with timers and bells"""
    
    # Signals
    exam_started = pyqtSignal(dict)  # Exam config
    exam_finished = pyqtSignal()
    
    def __init__(self, bell_player=None, parent=None):
        super().__init__(parent)
        self.bell_player = bell_player
        self.exam_config = None
        self.reading_timer = None
        self.exam_timer = None
        self.warning_played = False
        
        # Set up the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the widget UI"""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Exam header
        self.header_layout = QHBoxLayout()
        
        self.exam_title = QLabel("Examination Mode")
        self.exam_title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)
        
        self.current_time = QLabel()
        self.current_time.setStyleSheet("""
            font-size: 24px;
            color: #8080a0;
        """)
        
        self.header_layout.addWidget(self.exam_title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.current_time)
        
        # Timer container
        self.timer_container = QFrame()
        self.timer_container.setFrameShape(QFrame.StyledPanel)
        self.timer_container.setStyleSheet("""
            background-color: #1a1a2a;
            border-radius: 15px;
            border: 1px solid #353550;
            padding: 20px;
        """)
        
        self.timer_layout = QVBoxLayout(self.timer_container)
        
        # Status label
        self.status_label = QLabel("Configure and start the examination")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 18px;
            color: #00a0ff;
            margin-bottom: 20px;
        """)
        
        # Timers will be added when exam is configured
        
        self.timer_layout.addWidget(self.status_label)
        
        # Button panel
        self.button_panel = QFrame()
        self.button_layout = QHBoxLayout(self.button_panel)
        
        self.configure_button = QPushButton("Configure Exam")
        self.configure_button.clicked.connect(self.configure_exam)
        self.configure_button.setStyleSheet("""
            background-color: #00a0ff;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 16px;
        """)
        
        self.exit_button = QPushButton("Exit Exam Mode")
        self.exit_button.clicked.connect(self.exit_exam_mode)
        self.exit_button.setStyleSheet("""
            background-color: #ff5500;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 16px;
        """)
        self.exit_button.setEnabled(False)
        
        self.button_layout.addWidget(self.configure_button)
        self.button_layout.addWidget(self.exit_button)
        
        # Add components to main layout
        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.timer_container)
        self.layout.addWidget(self.button_panel)
        
        # Set up a timer to update the clock
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
        # Update clock immediately
        self.update_clock()
        
    def update_clock(self):
        """Update the current time display"""
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss AP")
        self.current_time.setText(current_time)
        
        # Check if a warning bell should be played
        if self.exam_config and self.exam_timer and not self.warning_played:
            if self.exam_timer.seconds_left <= self.exam_config["warning_bell"] * 60 and self.exam_config["warning_bell"] > 0:
                self.play_warning_bell()
                self.warning_played = True
        
    def configure_exam(self):
        """Configure the examination mode"""
        dialog = ExamConfigDialog(self)
        
        if dialog.exec_():
            # Get exam configuration
            self.exam_config = dialog.get_config()
            
            # Clear existing timers
            self.clear_timers()
            
            # Set up exam title
            self.exam_title.setText(self.exam_config["name"])
            
            # Create reading timer if needed
            if self.exam_config["reading_time"] > 0:
                self.reading_timer = ExamTimerWidget(
                    timer_id="reading",
                    name="Reading Time",
                    duration=self.exam_config["reading_time"],
                    parent=self
                )
                self.reading_timer.timer_complete.connect(self.on_reading_complete)
                self.timer_layout.addWidget(self.reading_timer)
            
            # Create exam timer
            self.exam_timer = ExamTimerWidget(
                timer_id="exam",
                name="Exam Time",
                duration=self.exam_config["duration"],
                parent=self
            )
            self.exam_timer.timer_complete.connect(self.on_exam_complete)
            self.timer_layout.addWidget(self.exam_timer)
            
            # Update status label
            if self.reading_timer:
                self.status_label.setText("Start reading time when ready")
                # Disable exam timer until reading is complete
                self.exam_timer.setEnabled(False)
            else:
                self.status_label.setText("Start exam when ready")
            
            # Configure buttons
            self.configure_button.setEnabled(False)
            self.exit_button.setEnabled(True)
            
            # Start automatically if configured
            if self.exam_config["auto_start"]:
                if self.reading_timer:
                    self.reading_timer.start_timer()
                else:
                    self.start_exam()
                    
            # Set display mode
            if self.exam_config["display_mode"] == "Full Screen":
                self.parent().showFullScreen()
            elif self.exam_config["display_mode"] == "Full Screen with Controls":
                self.parent().showMaximized()
                
            # Emit exam started signal
            self.exam_started.emit(self.exam_config)
            
    def clear_timers(self):
        """Clear all timers from the layout"""
        # Remove and delete existing timers
        if self.reading_timer:
            self.timer_layout.removeWidget(self.reading_timer)
            self.reading_timer.deleteLater()
            self.reading_timer = None
            
        if self.exam_timer:
            self.timer_layout.removeWidget(self.exam_timer)
            self.exam_timer.deleteLater()
            self.exam_timer = None
            
        self.warning_played = False
            
    def on_reading_complete(self, timer_id):
        """Handler for reading timer completion"""
        # Update status
        self.status_label.setText("Reading time complete. Start exam when ready.")
        
        # Enable exam timer
        self.exam_timer.setEnabled(True)
        
        # Play bell if configured
        if self.exam_config["play_start_bell"]:
            self.play_bell("reading_end")
            
    def on_exam_complete(self, timer_id):
        """Handler for exam timer completion"""
        # Update status
        self.status_label.setText("Examination complete!")
        
        # Play bell if configured
        if self.exam_config["play_end_bell"]:
            self.play_bell("exam_end")
            
        # Reset warning bell flag
        self.warning_played = False
        
        # Emit exam finished signal
        self.exam_finished.emit()
        
    def start_exam(self):
        """Start the examination timer"""
        if self.exam_timer:
            self.exam_timer.start_timer()
            
            # Update status
            self.status_label.setText("Examination in progress")
            
            # Play bell if configured
            if self.exam_config["play_start_bell"]:
                self.play_bell("exam_start")
                
    def play_warning_bell(self):
        """Play the warning bell"""
        self.play_bell("warning")
        
        # Update status label to indicate warning
        minutes = self.exam_config["warning_bell"]
        self.status_label.setText(f"Warning: {minutes} minute{'s' if minutes != 1 else ''} remaining!")
        self.status_label.setStyleSheet("""
            font-size: 18px;
            color: #ffaa00;
            margin-bottom: 20px;
            font-weight: bold;
        """)
        
    def play_bell(self, bell_type):
        """Play a bell sound based on the bell type and configuration"""
        if not self.bell_player:
            return
            
        # Determine which sound to play
        sound_name = self.exam_config["bell_sound"]
        
        # Map to actual sound file
        sound_files = {
            "Default Bell": "default.mp3",
            "Exam Bell": "exam_bell.mp3",
            "Soft Bell": "soft_bell.mp3",
            "Electronic Tone": "electronic_tone.mp3"
        }
        
        sound_file = sound_files.get(sound_name, "default.mp3")
        
        # Create a temporary Bell object for the player
        from core.scheduler import Bell
        
        bell = Bell(
            name=f"{self.exam_config['name']} - {bell_type}",
            time=QTime.currentTime(),
            sound=sound_file,
            volume=100,
            tts_message=None
        )
        
        # Play the bell
        self.bell_player.play_bell(bell)
        
    def exit_exam_mode(self):
        """Exit examination mode"""
        # Confirm if exam is in progress
        if self.exam_timer and self.exam_timer.running:
            if QMessageBox.question(
                self, "Exit Exam Mode",
                "Exam is still running. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No
            ) != QMessageBox.Yes:
                return
                
        # Clear timers
        self.clear_timers()
        
        # Reset UI
        self.exam_title.setText("Examination Mode")
        self.status_label.setText("Configure and start the examination")
        self.configure_button.setEnabled(True)
        self.exit_button.setEnabled(False)
        
        # Exit fullscreen if needed
        if self.parent() and (self.parent().isFullScreen() or self.parent().isMaximized()):
            self.parent().showNormal()
            
        # Emit exam finished signal
        self.exam_finished.emit()