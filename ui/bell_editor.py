from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTimeEdit,
    QPushButton, QComboBox, QSlider, QCheckBox, QColorDialog, QGroupBox,
    QFileDialog, QSpinBox, QTabWidget, QWidget, QScrollArea, QFrame,
    QGridLayout, QListWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QTime, QSize
from PyQt5.QtGui import QColor, QIcon

import os
import sys

class BellEditor(QDialog):
    def __init__(self, parent=None, bell=None, sounds_dir="assets/sounds"):
        super().__init__(parent)
        self.setWindowTitle("Bell Editor")
        self.setMinimumSize(500, 600)
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.sounds_dir = sounds_dir
        self.bell = bell
        
        # Set up the UI
        self.setup_ui()
        
        # Fill form if editing existing bell
        if bell:
            self.populate_form()
        
    def setup_ui(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Basic tab
        self.basic_tab = QWidget()
        self.basic_layout = QVBoxLayout(self.basic_tab)
        
        # Bell name
        self.name_layout = QHBoxLayout()
        self.name_label = QLabel("Bell Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter bell name")
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_edit)
        self.basic_layout.addLayout(self.name_layout)
        
        # Time
        self.time_layout = QHBoxLayout()
        self.time_label = QLabel("Time:")
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("hh:mm AP")
        self.time_edit.setTime(QTime.currentTime())
        self.time_layout.addWidget(self.time_label)
        self.time_layout.addWidget(self.time_edit)
        self.basic_layout.addLayout(self.time_layout)
        
        # Category
        self.category_layout = QHBoxLayout()
        self.category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        self.category_combo.addItems(["School", "Class", "Break", "Exam", "Custom"])
        self.category_layout.addWidget(self.category_label)
        self.category_layout.addWidget(self.category_combo)
        self.basic_layout.addLayout(self.category_layout)
        
        # Days
        self.days_group = QGroupBox("Days")
        self.days_layout = QVBoxLayout(self.days_group)
        
        self.weekdays_layout = QHBoxLayout()
        self.monday_cb = QCheckBox("Monday")
        self.tuesday_cb = QCheckBox("Tuesday")
        self.wednesday_cb = QCheckBox("Wednesday")
        self.thursday_cb = QCheckBox("Thursday")
        self.friday_cb = QCheckBox("Friday")
        
        # By default, check weekdays
        self.monday_cb.setChecked(True)
        self.tuesday_cb.setChecked(True)
        self.wednesday_cb.setChecked(True)
        self.thursday_cb.setChecked(True)
        self.friday_cb.setChecked(True)
        
        self.weekdays_layout.addWidget(self.monday_cb)
        self.weekdays_layout.addWidget(self.tuesday_cb)
        self.weekdays_layout.addWidget(self.wednesday_cb)
        self.weekdays_layout.addWidget(self.thursday_cb)
        self.weekdays_layout.addWidget(self.friday_cb)
        
        self.weekend_layout = QHBoxLayout()
        self.saturday_cb = QCheckBox("Saturday")
        self.sunday_cb = QCheckBox("Sunday")
        self.weekend_layout.addWidget(self.saturday_cb)
        self.weekend_layout.addWidget(self.sunday_cb)
        
        self.days_layout.addLayout(self.weekdays_layout)
        self.days_layout.addLayout(self.weekend_layout)
        
        self.basic_layout.addWidget(self.days_group)
        
        # Color
        self.color_layout = QHBoxLayout()
        self.color_label = QLabel("Color:")
        self.color_button = QPushButton()
        self.color_button.setFixedSize(40, 25)
        self.color = QColor("#00a0ff")  # Default color
        self.color_button.setStyleSheet(f"background-color: {self.color.name()}")
        self.color_button.clicked.connect(self.choose_color)
        self.color_layout.addWidget(self.color_label)
        self.color_layout.addWidget(self.color_button)
        self.basic_layout.addLayout(self.color_layout)
        
        # Enabled
        self.enabled_cb = QCheckBox("Bell Enabled")
        self.enabled_cb.setChecked(True)
        self.basic_layout.addWidget(self.enabled_cb)
        
        # Add the basic tab
        self.tabs.addTab(self.basic_tab, "Basic Settings")
        
        # Sound tab
        self.sound_tab = QWidget()
        self.sound_layout = QVBoxLayout(self.sound_tab)
        
        # Sound file
        self.sound_layout = QVBoxLayout(self.sound_tab)
        
        self.sound_file_layout = QHBoxLayout()
        self.sound_label = QLabel("Sound File:")
        self.sound_combo = QComboBox()
        
        # Populate sound files
        self.populate_sound_files()
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_sound)
        self.test_button = QPushButton("Test")
        self.test_button.clicked.connect(self.test_sound)
        
        self.sound_file_layout.addWidget(self.sound_label)
        self.sound_file_layout.addWidget(self.sound_combo)
        self.sound_file_layout.addWidget(self.browse_button)
        self.sound_file_layout.addWidget(self.test_button)
        
        self.sound_layout.addLayout(self.sound_file_layout)
        
        # Volume
        self.volume_layout = QHBoxLayout()
        self.volume_label = QLabel("Volume:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_value = QLabel("100%")
        self.volume_slider.valueChanged.connect(self.update_volume_label)
        
        self.volume_layout.addWidget(self.volume_label)
        self.volume_layout.addWidget(self.volume_slider)
        self.volume_layout.addWidget(self.volume_value)
        
        self.sound_layout.addLayout(self.volume_layout)
        
        # Special options
        self.sound_options_group = QGroupBox("Sound Options")
        self.sound_options_layout = QVBoxLayout(self.sound_options_group)
        
        self.repeat_cb = QCheckBox("Repeat Sound Until Stopped")
        self.silent_cb = QCheckBox("Silent Bell (Visual Only)")
        self.urgent_cb = QCheckBox("Urgent Bell (Full Screen Alert)")
        
        self.sound_options_layout.addWidget(self.repeat_cb)
        self.sound_options_layout.addWidget(self.silent_cb)
        self.sound_options_layout.addWidget(self.urgent_cb)
        
        self.sound_layout.addWidget(self.sound_options_group)
        
        # TTS Message
        self.tts_group = QGroupBox("Text-to-Speech Message")
        self.tts_layout = QVBoxLayout(self.tts_group)
        
        self.tts_edit = QLineEdit()
        self.tts_edit.setPlaceholderText("Enter message to be spoken when bell rings")
        
        self.tts_layout.addWidget(self.tts_edit)
        
        self.sound_layout.addWidget(self.tts_group)
        
        # Add the sound tab
        self.tabs.addTab(self.sound_tab, "Sound & Alerts")
        
        # Add tabs to main layout
        self.layout.addWidget(self.tabs)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Save Bell")
        self.save_button.clicked.connect(self.save_bell)
        self.save_button.setStyleSheet("""
            background-color: #00a0ff;
            color: white;
            font-weight: bold;
            padding: 8px 16px;
        """)
        
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.save_button)
        
        self.layout.addLayout(self.button_layout)
    
    def populate_sound_files(self):
        """Populate the sound files dropdown"""
        self.sound_combo.clear()
        
        # Add default option
        self.sound_combo.addItem("default.mp3")
        
        # Check if sounds directory exists
        if os.path.exists(self.sounds_dir):
            for file in os.listdir(self.sounds_dir):
                if file.endswith(('.mp3', '.wav')) and file != "default.mp3":
                    self.sound_combo.addItem(file)
    
    def update_volume_label(self):
        """Update volume percentage label"""
        value = self.volume_slider.value()
        self.volume_value.setText(f"{value}%")
    
    def choose_color(self):
        """Open color dialog and set bell color"""
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()}")
    
    def browse_sound(self):
        """Browse for a sound file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Sound File", "", "Audio Files (*.mp3 *.wav)"
        )
        
        if file_path:
            # Copy file to sounds directory
            import shutil
            os.makedirs(self.sounds_dir, exist_ok=True)
            
            # Get just the filename
            filename = os.path.basename(file_path)
            
            # Copy file
            dest_path = os.path.join(self.sounds_dir, filename)
            try:
                shutil.copy2(file_path, dest_path)
                
                # Refresh sound files and select new one
                self.populate_sound_files()
                self.sound_combo.setCurrentText(filename)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not copy sound file: {str(e)}")
    
    def test_sound(self):
        """Test the selected sound"""
        sound_file = self.sound_combo.currentText()
        volume = self.volume_slider.value()
        
        # Try importing bell player module
        try:
            from core.bell_player import BellPlayer
            
            player = BellPlayer(self.sounds_dir)
            player.test_sound(sound_file, volume)
        except ImportError:
            QMessageBox.warning(self, "Error", "Bell player module not available")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not play sound: {str(e)}")
    
    def populate_form(self):
        """Fill form with bell data if editing existing bell"""
        if not self.bell:
            return
            
        # Basic info
        self.name_edit.setText(self.bell.name)
        self.time_edit.setTime(self.bell.time)
        self.category_combo.setCurrentText(self.bell.category)
        
        # Days
        self.monday_cb.setChecked("Monday" in self.bell.days)
        self.tuesday_cb.setChecked("Tuesday" in self.bell.days)
        self.wednesday_cb.setChecked("Wednesday" in self.bell.days)
        self.thursday_cb.setChecked("Thursday" in self.bell.days)
        self.friday_cb.setChecked("Friday" in self.bell.days)
        self.saturday_cb.setChecked("Saturday" in self.bell.days)
        self.sunday_cb.setChecked("Sunday" in self.bell.days)
        
        # Color
        self.color = QColor(self.bell.color)
        self.color_button.setStyleSheet(f"background-color: {self.color.name()}")
        
        # Enabled
        self.enabled_cb.setChecked(self.bell.enabled)
        
        # Sound
        self.sound_combo.setCurrentText(self.bell.sound)
        self.volume_slider.setValue(self.bell.volume)
        self.update_volume_label()
        
        # Options
        self.repeat_cb.setChecked(self.bell.repeat)
        self.silent_cb.setChecked(self.bell.silent)
        self.urgent_cb.setChecked(self.bell.urgent)
        
        # TTS
        if self.bell.tts_message:
            self.tts_edit.setText(self.bell.tts_message)
    
    def save_bell(self):
        """Save bell data and close dialog"""
        # Validate bell name
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Bell name cannot be empty")
            return
        
        # Get selected days
        days = []
        if self.monday_cb.isChecked():
            days.append("Monday")
        if self.tuesday_cb.isChecked():
            days.append("Tuesday")
        if self.wednesday_cb.isChecked():
            days.append("Wednesday")
        if self.thursday_cb.isChecked():
            days.append("Thursday")
        if self.friday_cb.isChecked():
            days.append("Friday")
        if self.saturday_cb.isChecked():
            days.append("Saturday")
        if self.sunday_cb.isChecked():
            days.append("Sunday")
        
        # Validate at least one day is selected
        if not days:
            QMessageBox.warning(self, "Error", "Please select at least one day")
            return
        
        # Create bell data dictionary
        self.bell_data = {
            "name": name,
            "time": self.time_edit.time(),
            "sound": self.sound_combo.currentText(),
            "days": days,
            "category": self.category_combo.currentText(),
            "color": self.color.name(),
            "volume": self.volume_slider.value(),
            "enabled": self.enabled_cb.isChecked(),
            "repeat": self.repeat_cb.isChecked(),
            "silent": self.silent_cb.isChecked(),
            "urgent": self.urgent_cb.isChecked(),
            "tts_message": self.tts_edit.text().strip() or None
        }
        
        # Accept dialog
        self.accept()