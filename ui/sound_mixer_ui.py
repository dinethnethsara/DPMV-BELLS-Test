from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QSlider, QFileDialog, QComboBox, QMessageBox,
    QListWidget, QListWidgetItem, QMenu, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QTabWidget, QSplitter, QDoubleSpinBox,
    QProgressBar, QLineEdit, QColorDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette

import os
from core.sound_mixer import SoundMixer, SoundEffect

class SoundLayerItem(QFrame):
    """Widget for a single sound layer in the mixer"""
    
    # Signals
    layer_changed = pyqtSignal(int)  # Layer index
    layer_removed = pyqtSignal(int)  # Layer index
    
    def __init__(self, layer_index, sound_file, volume=100, parent=None, sounds_dir="assets/sounds"):
        super().__init__(parent)
        self.layer_index = layer_index
        self.sound_file = sound_file
        self.volume = volume
        self.sounds_dir = sounds_dir
        self.effects = []
        
        # Set up the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the widget UI"""
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 5px;
            border: 1px solid #353550;
            padding: 5px;
        """)
        
        # Main layout
        self.layout = QHBoxLayout(self)
        
        # Layer number and name
        self.title_layout = QVBoxLayout()
        
        self.layer_number = QLabel(f"Layer {self.layer_index + 1}")
        self.layer_number.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #00a0ff;
        """)
        
        self.sound_name = QLabel(os.path.basename(self.sound_file))
        self.sound_name.setStyleSheet("""
            font-size: 14px;
            color: white;
        """)
        
        self.title_layout.addWidget(self.layer_number)
        self.title_layout.addWidget(self.sound_name)
        
        # Volume control
        self.volume_layout = QVBoxLayout()
        
        self.volume_label = QLabel("Volume:")
        self.volume_label.setStyleSheet("color: white;")
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.volume)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        
        self.volume_layout.addWidget(self.volume_label)
        self.volume_layout.addWidget(self.volume_slider)
        
        # Effects
        self.effects_layout = QVBoxLayout()
        
        self.effects_label = QLabel("Effects:")
        self.effects_label.setStyleSheet("color: white;")
        
        self.effects_combo = QComboBox()
        self.effects_combo.addItems(["None", "Fade", "Echo", "Pitch"])
        self.effects_combo.currentIndexChanged.connect(self.on_effect_selected)
        
        self.effects_layout.addWidget(self.effects_label)
        self.effects_layout.addWidget(self.effects_combo)
        
        # Buttons
        self.button_layout = QVBoxLayout()
        
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(30, 30)
        self.play_button.clicked.connect(self.play_sound)
        
        self.remove_button = QPushButton("✕")
        self.remove_button.setFixedSize(30, 30)
        self.remove_button.clicked.connect(self.remove_layer)
        self.remove_button.setStyleSheet("""
            background-color: #ff5500;
            color: white;
            border-radius: 15px;
        """)
        
        self.button_layout.addWidget(self.play_button)
        self.button_layout.addWidget(self.remove_button)
        
        # Add all layouts to main layout
        self.layout.addLayout(self.title_layout)
        self.layout.addLayout(self.volume_layout)
        self.layout.addLayout(self.effects_layout)
        self.layout.addLayout(self.button_layout)
        
    def on_volume_changed(self, value):
        """Handle volume slider change"""
        self.volume = value
        self.layer_changed.emit(self.layer_index)
        
    def on_effect_selected(self, index):
        """Handle effect selection"""
        effect_type = self.effects_combo.currentText()
        
        if effect_type == "None":
            self.effects = []
        elif effect_type == "Fade":
            self.effects = [SoundEffect("Fade", "fade", {"fade_in": 0.5, "fade_out": 0.5})]
        elif effect_type == "Echo":
            self.effects = [SoundEffect("Echo", "echo", {"delay": 0.3, "decay": 0.5})]
        elif effect_type == "Pitch":
            self.effects = [SoundEffect("Pitch", "pitch", {"semitones": 2})]
            
        self.layer_changed.emit(self.layer_index)
        
    def play_sound(self):
        """Play just this sound layer"""
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
                
            sound_path = os.path.join(self.sounds_dir, self.sound_file)
            if os.path.exists(sound_path):
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.set_volume(self.volume / 100)
                pygame.mixer.music.play()
        except Exception as e:
            print(f"Error playing sound: {e}")
            
    def remove_layer(self):
        """Remove this layer"""
        self.layer_removed.emit(self.layer_index)
        
    def get_data(self):
        """Get this layer's data"""
        return {
            "sound_file": self.sound_file,
            "volume": self.volume,
            "effects": self.effects
        }


class SoundMixerUI(QWidget):
    """UI for mixing and layering bell sounds"""
    
    sound_mixed = pyqtSignal(str)  # Path to mixed sound
    
    def __init__(self, sounds_dir="assets/sounds", parent=None):
        super().__init__(parent)
        self.sounds_dir = sounds_dir
        self.layers = []
        self.sound_mixer = SoundMixer(sounds_dir)
        
        # Set up the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the widget UI"""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Title and description
        self.title = QLabel("Sound Mixer")
        self.title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
        """)
        
        self.description = QLabel(
            "Create custom bell sounds by layering multiple sounds and applying effects."
        )
        self.description.setStyleSheet("color: #8080a0;")
        self.description.setWordWrap(True)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        
        self.add_layer_button = QPushButton("+ Add Sound Layer")
        self.add_layer_button.clicked.connect(self.add_layer)
        self.add_layer_button.setStyleSheet("""
            background-color: #00a0ff;
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
        """)
        
        self.mix_button = QPushButton("Mix Sounds")
        self.mix_button.clicked.connect(self.mix_sounds)
        self.mix_button.setStyleSheet("""
            background-color: #00ff99;
            color: black;
            border-radius: 5px;
            padding: 5px 10px;
            font-weight: bold;
        """)
        self.mix_button.setEnabled(False)
        
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_layers)
        self.clear_button.setStyleSheet("""
            background-color: #ff5500;
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
        """)
        
        self.button_layout.addWidget(self.add_layer_button)
        self.button_layout.addWidget(self.mix_button)
        self.button_layout.addWidget(self.clear_button)
        
        # Layers container
        self.layers_scroll = QScrollArea()
        self.layers_scroll.setWidgetResizable(True)
        self.layers_scroll.setStyleSheet("""
            background-color: #1a1a2a;
            border-radius: 10px;
            border: 1px solid #353550;
        """)
        
        self.layers_container = QWidget()
        self.layers_layout = QVBoxLayout(self.layers_container)
        self.layers_layout.setAlignment(Qt.AlignTop)
        self.layers_layout.setContentsMargins(10, 10, 10, 10)
        self.layers_layout.setSpacing(10)
        
        self.layers_scroll.setWidget(self.layers_container)
        
        # Output panel
        self.output_panel = QFrame()
        self.output_panel.setFrameShape(QFrame.StyledPanel)
        self.output_panel.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
            border: 1px solid #353550;
            padding: 10px;
        """)
        
        self.output_layout = QVBoxLayout(self.output_panel)
        
        self.output_title = QLabel("Output Sound")
        self.output_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #00a0ff;
        """)
        
        self.output_name = QLineEdit("mixed_sound.wav")
        
        self.output_play_button = QPushButton("Play Mixed Sound")
        self.output_play_button.clicked.connect(self.play_mixed_sound)
        self.output_play_button.setEnabled(False)
        
        self.output_save_button = QPushButton("Save As...")
        self.output_save_button.clicked.connect(self.save_mixed_sound)
        self.output_save_button.setEnabled(False)
        
        self.output_layout.addWidget(self.output_title)
        self.output_layout.addWidget(self.output_name)
        self.output_layout.addWidget(self.output_play_button)
        self.output_layout.addWidget(self.output_save_button)
        
        # Add all components to main layout
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.description)
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.layers_scroll)
        self.layout.addWidget(self.output_panel)
        
        # Connect sound mixer signals
        self.sound_mixer.mix_completed.connect(self.on_mix_completed)
        self.sound_mixer.mix_failed.connect(self.on_mix_failed)
        
    def add_layer(self):
        """Add a new sound layer"""
        # Show file dialog to select sound
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Sound Files (*.wav *.mp3)")
        dialog.setDirectory(self.sounds_dir)
        
        if dialog.exec_():
            sound_file = dialog.selectedFiles()[0]
            
            # Check if it's in the sounds directory
            if os.path.dirname(sound_file) != self.sounds_dir:
                # Copy to sounds directory
                import shutil
                base_name = os.path.basename(sound_file)
                dest_path = os.path.join(self.sounds_dir, base_name)
                
                # Check if already exists
                if os.path.exists(dest_path):
                    result = QMessageBox.question(
                        self, "File Exists",
                        f"File {base_name} already exists in sounds directory. Use existing file?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if result == QMessageBox.Yes:
                        sound_file = base_name
                    else:
                        return
                else:
                    # Copy file
                    shutil.copy2(sound_file, dest_path)
                    sound_file = base_name
            else:
                # Use relative path
                sound_file = os.path.basename(sound_file)
                
            # Add layer widget
            layer_widget = SoundLayerItem(
                len(self.layers),
                sound_file,
                parent=self,
                sounds_dir=self.sounds_dir
            )
            layer_widget.layer_changed.connect(self.on_layer_changed)
            layer_widget.layer_removed.connect(self.on_layer_removed)
            
            self.layers_layout.addWidget(layer_widget)
            self.layers.append(layer_widget)
            
            # Enable mix button if there's at least one layer
            self.mix_button.setEnabled(True)
            
    def on_layer_changed(self, layer_index):
        """Handle layer parameter changes"""
        # Nothing to do here, data is stored in the layer widget
        pass
        
    def on_layer_removed(self, layer_index):
        """Handle layer removal"""
        # Get the widget to remove
        widget_to_remove = None
        for i, layer in enumerate(self.layers):
            if layer.layer_index == layer_index:
                widget_to_remove = layer
                break
                
        if not widget_to_remove:
            return
            
        # Remove from layout and list
        self.layers_layout.removeWidget(widget_to_remove)
        self.layers.remove(widget_to_remove)
        widget_to_remove.deleteLater()
        
        # Renumber remaining layers
        for i, layer in enumerate(self.layers):
            layer.layer_index = i
            layer.layer_number.setText(f"Layer {i + 1}")
            
        # Disable mix button if no layers left
        if not self.layers:
            self.mix_button.setEnabled(False)
            
    def mix_sounds(self):
        """Mix the sound layers"""
        if not self.layers:
            return
            
        # Get data from each layer
        sound_files = []
        volumes = []
        all_effects = []
        
        for layer in self.layers:
            data = layer.get_data()
            sound_files.append(data["sound_file"])
            volumes.append(data["volume"])
            all_effects.extend(data["effects"])
            
        # Get output name
        output_name = self.output_name.text()
        if not output_name.endswith(('.wav', '.mp3')):
            output_name += '.wav'
            
        output_path = os.path.join(self.sounds_dir, output_name)
        
        # Perform the mix
        self.sound_mixer.create_layered_sound(
            sound_files=sound_files,
            volumes=volumes,
            output_path=output_path,
            effects=all_effects
        )
        
    def on_mix_completed(self, output_path):
        """Handle successful mix"""
        self.output_play_button.setEnabled(True)
        self.output_save_button.setEnabled(True)
        
        QMessageBox.information(self, "Mix Complete", 
                               f"Sounds have been mixed successfully to {os.path.basename(output_path)}")
                               
        # Emit signal
        self.sound_mixed.emit(output_path)
        
    def on_mix_failed(self, error_message):
        """Handle mix failure"""
        QMessageBox.warning(self, "Mix Failed", f"Failed to mix sounds: {error_message}")
        
    def play_mixed_sound(self):
        """Play the mixed sound"""
        output_name = self.output_name.text()
        if not output_name.endswith(('.wav', '.mp3')):
            output_name += '.wav'
            
        output_path = os.path.join(self.sounds_dir, output_name)
        
        if not os.path.exists(output_path):
            QMessageBox.warning(self, "File Not Found", 
                               f"Mixed sound file not found: {output_path}")
            return
            
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
                
            pygame.mixer.music.load(output_path)
            pygame.mixer.music.play()
        except Exception as e:
            QMessageBox.warning(self, "Playback Error", f"Error playing sound: {str(e)}")
            
    def save_mixed_sound(self):
        """Save the mixed sound to a different location"""
        output_name = self.output_name.text()
        if not output_name.endswith(('.wav', '.mp3')):
            output_name += '.wav'
            
        source_path = os.path.join(self.sounds_dir, output_name)
        
        if not os.path.exists(source_path):
            QMessageBox.warning(self, "File Not Found", 
                               f"Mixed sound file not found: {source_path}")
            return
            
        # Ask user for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Mixed Sound", output_name, "Sound Files (*.wav *.mp3)"
        )
        
        if not file_path:
            return
            
        try:
            import shutil
            shutil.copy2(source_path, file_path)
            
            QMessageBox.information(self, "Save Complete", 
                                   f"Sound saved to {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Error saving sound: {str(e)}")
            
    def clear_layers(self):
        """Remove all layers"""
        if not self.layers:
            return
            
        # Confirm with user
        result = QMessageBox.question(
            self, "Clear All Layers",
            "Are you sure you want to remove all sound layers?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if result != QMessageBox.Yes:
            return
            
        # Remove all layers
        for layer in self.layers:
            self.layers_layout.removeWidget(layer)
            layer.deleteLater()
            
        self.layers = []
        
        # Disable mix button
        self.mix_button.setEnabled(False)