from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QSlider, QFileDialog, QComboBox, QMessageBox,
    QListWidget, QListWidgetItem, QMenu, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QTabWidget, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter

import os
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import wave
import contextlib

class WaveformCanvas(FigureCanvas):
    """Canvas for displaying audio waveform"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#1e1e2e')
        
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#1e1e2e')
        self.axes.tick_params(axis='x', colors='white')
        self.axes.tick_params(axis='y', colors='white')
        self.axes.spines['bottom'].set_color('#353550')
        self.axes.spines['top'].set_color('#353550')
        self.axes.spines['left'].set_color('#353550')
        self.axes.spines['right'].set_color('#353550')
        self.axes.set_title('Waveform', color='white')
        self.axes.set_xlabel('Time (s)', color='white')
        self.axes.set_ylabel('Amplitude', color='white')
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.setStyleSheet("background-color: #1e1e2e;")
        
    def plot_waveform(self, audio_path):
        """Plot audio waveform from file"""
        self.axes.clear()
        
        try:
            # Read audio file
            with contextlib.closing(wave.open(audio_path, 'rb')) as wf:
                # Get parameters
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                sample_rate = wf.getframerate()
                num_frames = wf.getnframes()
                
                # Read all frames
                buffer = wf.readframes(num_frames)
                
                # Convert buffer to numpy array
                if sample_width == 1:
                    dtype = np.uint8
                elif sample_width == 2:
                    dtype = np.int16
                elif sample_width == 4:
                    dtype = np.int32
                else:
                    raise ValueError(f"Unsupported sample width: {sample_width}")
                    
                # Convert to numpy array
                samples = np.frombuffer(buffer, dtype=dtype)
                
                # If stereo, take just left channel
                if num_channels == 2:
                    samples = samples[::2]
                    
                # Create time axis
                duration = num_frames / sample_rate
                time = np.linspace(0, duration, num=len(samples))
                
                # Plot waveform
                self.axes.plot(time, samples, color='#00a0ff')
                self.axes.set_xlim(0, duration)
                
                # Set titles
                self.axes.set_title('Waveform', color='white')
                self.axes.set_xlabel('Time (s)', color='white')
                self.axes.set_ylabel('Amplitude', color='white')
                
                self.fig.tight_layout()
                self.draw()
                return True
        
        except Exception as e:
            print(f"Error plotting waveform: {e}")
            return False


class SpectrogramCanvas(FigureCanvas):
    """Canvas for displaying audio spectrogram"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#1e1e2e')
        
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor('#1e1e2e')
        self.axes.tick_params(axis='x', colors='white')
        self.axes.tick_params(axis='y', colors='white')
        self.axes.spines['bottom'].set_color('#353550')
        self.axes.spines['top'].set_color('#353550')
        self.axes.spines['left'].set_color('#353550')
        self.axes.spines['right'].set_color('#353550')
        self.axes.set_title('Spectrogram', color='white')
        self.axes.set_xlabel('Time (s)', color='white')
        self.axes.set_ylabel('Frequency (Hz)', color='white')
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.setStyleSheet("background-color: #1e1e2e;")
        
    def plot_spectrogram(self, audio_path):
        """Plot audio spectrogram from file"""
        self.axes.clear()
        
        try:
            # Read audio file
            with contextlib.closing(wave.open(audio_path, 'rb')) as wf:
                # Get parameters
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                sample_rate = wf.getframerate()
                num_frames = wf.getnframes()
                
                # Read all frames
                buffer = wf.readframes(num_frames)
                
                # Convert buffer to numpy array
                if sample_width == 1:
                    dtype = np.uint8
                elif sample_width == 2:
                    dtype = np.int16
                elif sample_width == 4:
                    dtype = np.int32
                else:
                    raise ValueError(f"Unsupported sample width: {sample_width}")
                    
                # Convert to numpy array
                samples = np.frombuffer(buffer, dtype=dtype)
                
                # If stereo, take just left channel
                if num_channels == 2:
                    samples = samples[::2]
                    
                # Plot spectrogram
                self.axes.specgram(samples, Fs=sample_rate, cmap='viridis')
                
                # Set titles
                self.axes.set_title('Spectrogram', color='white')
                self.axes.set_xlabel('Time (s)', color='white')
                self.axes.set_ylabel('Frequency (Hz)', color='white')
                
                # Add colorbar
                cbar = self.fig.colorbar(self.axes.images[0])
                cbar.ax.tick_params(labelcolor='white')
                cbar.set_label('Intensity (dB)', color='white')
                
                self.fig.tight_layout()
                self.draw()
                return True
        
        except Exception as e:
            print(f"Error plotting spectrogram: {e}")
            return False


class SoundVisualizerWidget(QWidget):
    """Widget for visualizing sound files with waveform and spectrogram"""
    
    sound_selected = pyqtSignal(str)  # Path to selected sound
    
    def __init__(self, sounds_dir="assets/sounds", parent=None):
        super().__init__(parent)
        self.sounds_dir = sounds_dir
        self.current_sound = None
        
        # Set up the UI
        self.setup_ui()
        
        # Load sounds
        self.load_sounds()
        
    def setup_ui(self):
        """Set up the widget UI"""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Add header with title and controls
        self.header_layout = QHBoxLayout()
        
        self.title = QLabel("Sound Visualizer")
        self.title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)
        
        self.import_button = QPushButton("Import Sound")
        self.import_button.clicked.connect(self.import_sound)
        self.import_button.setStyleSheet("""
            background-color: #00a0ff;
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
        """)
        
        self.export_button = QPushButton("Export Image")
        self.export_button.clicked.connect(self.export_visualization)
        self.export_button.setStyleSheet("""
            background-color: #00ff99;
            color: black;
            border-radius: 5px;
            padding: 5px 10px;
        """)
        self.export_button.setEnabled(False)
        
        self.header_layout.addWidget(self.title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.import_button)
        self.header_layout.addWidget(self.export_button)
        
        # Create a splitter for sound list and visualizations
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Sound list panel
        self.list_panel = QFrame()
        self.list_panel.setFrameShape(QFrame.StyledPanel)
        self.list_panel.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
            border: 1px solid #353550;
        """)
        self.list_layout = QVBoxLayout(self.list_panel)
        
        self.list_label = QLabel("Available Sounds")
        self.list_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #00a0ff;
        """)
        
        self.sound_list = QListWidget()
        self.sound_list.setStyleSheet("""
            background-color: #252535;
            border-radius: 5px;
            border: 1px solid #353550;
            padding: 5px;
            color: white;
        """)
        self.sound_list.itemSelectionChanged.connect(self.on_sound_selected)
        self.sound_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sound_list.customContextMenuRequested.connect(self.show_context_menu)
        
        self.list_layout.addWidget(self.list_label)
        self.list_layout.addWidget(self.sound_list)
        
        # Visualization panel
        self.viz_panel = QFrame()
        self.viz_panel.setFrameShape(QFrame.StyledPanel)
        self.viz_panel.setStyleSheet("""
            background-color: #1e1e2e;
            border-radius: 10px;
            border: 1px solid #353550;
        """)
        self.viz_layout = QVBoxLayout(self.viz_panel)
        
        # Sound info
        self.sound_info = QLabel("Select a sound to visualize")
        self.sound_info.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #00a0ff;
            padding: 10px;
        """)
        self.sound_info.setAlignment(Qt.AlignCenter)
        
        # Play controls
        self.controls_layout = QHBoxLayout()
        
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_sound)
        self.play_button.setEnabled(False)
        self.play_button.setStyleSheet("""
            background-color: #00ff99;
            color: black;
            border-radius: 5px;
            padding: 5px 20px;
            font-weight: bold;
        """)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_sound)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            background-color: #ff5500;
            color: white;
            border-radius: 5px;
            padding: 5px 20px;
            font-weight: bold;
        """)
        
        self.loop_checkbox = QCheckBox("Loop")
        self.loop_checkbox.setStyleSheet("color: white;")
        
        self.controls_layout.addWidget(self.play_button)
        self.controls_layout.addWidget(self.stop_button)
        self.controls_layout.addWidget(self.loop_checkbox)
        self.controls_layout.addStretch()
        
        # Create visualization tabs
        self.viz_tabs = QTabWidget()
        self.viz_tabs.setStyleSheet("""
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
        
        # Waveform tab
        self.waveform_tab = QWidget()
        self.waveform_layout = QVBoxLayout(self.waveform_tab)
        self.waveform_canvas = WaveformCanvas(self)
        self.waveform_layout.addWidget(self.waveform_canvas)
        self.viz_tabs.addTab(self.waveform_tab, "Waveform")
        
        # Spectrogram tab
        self.spectrogram_tab = QWidget()
        self.spectrogram_layout = QVBoxLayout(self.spectrogram_tab)
        self.spectrogram_canvas = SpectrogramCanvas(self)
        self.spectrogram_layout.addWidget(self.spectrogram_canvas)
        self.viz_tabs.addTab(self.spectrogram_tab, "Spectrogram")
        
        # Add elements to visualization panel
        self.viz_layout.addWidget(self.sound_info)
        self.viz_layout.addLayout(self.controls_layout)
        self.viz_layout.addWidget(self.viz_tabs)
        
        # Add panels to splitter
        self.splitter.addWidget(self.list_panel)
        self.splitter.addWidget(self.viz_panel)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)
        
        # Add components to main layout
        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.splitter)
        
        # Initialize pygame mixer for playback
        try:
            import pygame
            pygame.mixer.init()
            self.pygame_available = True
        except ImportError:
            self.pygame_available = False
            QMessageBox.warning(self, "Pygame Not Available", 
                               "Pygame is not available. Sound playback will be disabled.")
        
    def load_sounds(self):
        """Load sound files from the sounds directory"""
        self.sound_list.clear()
        
        if not os.path.exists(self.sounds_dir):
            os.makedirs(self.sounds_dir, exist_ok=True)
            return
            
        sound_files = []
        for file in os.listdir(self.sounds_dir):
            if file.lower().endswith(('.wav', '.mp3')):
                sound_files.append(file)
                
        for sound_file in sorted(sound_files):
            self.sound_list.addItem(sound_file)
            
    def on_sound_selected(self):
        """Handle sound selection from the list"""
        items = self.sound_list.selectedItems()
        if not items:
            return
            
        sound_file = items[0].text()
        sound_path = os.path.join(self.sounds_dir, sound_file)
        
        if not os.path.exists(sound_path):
            QMessageBox.warning(self, "File Not Found", f"Sound file not found: {sound_path}")
            return
            
        self.current_sound = sound_path
        
        # Update info
        self.sound_info.setText(f"Sound: {sound_file}")
        
        # Enable buttons
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.export_button.setEnabled(True)
        
        # Visualize the sound
        self.visualize_sound(sound_path)
        
        # Emit signal
        self.sound_selected.emit(sound_path)
        
    def visualize_sound(self, sound_path):
        """Generate visualizations for the selected sound"""
        # Plot waveform
        self.waveform_canvas.plot_waveform(sound_path)
        
        # Plot spectrogram
        self.spectrogram_canvas.plot_spectrogram(sound_path)
        
    def play_sound(self):
        """Play the selected sound"""
        if not self.current_sound or not self.pygame_available:
            return
            
        try:
            import pygame
            
            # Stop any currently playing sound
            self.stop_sound()
            
            # Load and play the sound
            pygame.mixer.music.load(self.current_sound)
            
            # Set looping if checked
            if self.loop_checkbox.isChecked():
                pygame.mixer.music.play(-1)  # Loop indefinitely
            else:
                pygame.mixer.music.play()
                
            # Update buttons
            self.play_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
        except Exception as e:
            QMessageBox.warning(self, "Playback Error", f"Error playing sound: {str(e)}")
            
    def stop_sound(self):
        """Stop sound playback"""
        if not self.pygame_available:
            return
            
        try:
            import pygame
            
            pygame.mixer.music.stop()
            
            # Update buttons
            self.play_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            
        except Exception as e:
            QMessageBox.warning(self, "Playback Error", f"Error stopping sound: {str(e)}")
            
    def import_sound(self):
        """Import a sound file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Sound File", "", "Audio Files (*.wav *.mp3)"
        )
        
        if not file_path:
            return
            
        # Copy file to sounds directory
        import shutil
        
        # Ensure sounds directory exists
        os.makedirs(self.sounds_dir, exist_ok=True)
        
        # Extract file name
        file_name = os.path.basename(file_path)
        
        # Create destination path
        dest_path = os.path.join(self.sounds_dir, file_name)
        
        # Check if file already exists
        if os.path.exists(dest_path):
            if QMessageBox.question(
                self, "File Exists",
                f"File '{file_name}' already exists. Overwrite?",
                QMessageBox.Yes | QMessageBox.No
            ) != QMessageBox.Yes:
                return
                
        try:
            # Copy the file
            shutil.copy2(file_path, dest_path)
            
            # Reload sounds
            self.load_sounds()
            
            # Select the new sound
            for i in range(self.sound_list.count()):
                if self.sound_list.item(i).text() == file_name:
                    self.sound_list.setCurrentRow(i)
                    break
                    
        except Exception as e:
            QMessageBox.warning(self, "Import Error", f"Error importing sound: {str(e)}")
            
    def export_visualization(self):
        """Export current visualization as an image"""
        if not self.current_sound:
            return
            
        # Determine which tab is currently active
        current_tab = self.viz_tabs.currentIndex()
        
        # Get file name suggestion
        sound_name = os.path.basename(self.current_sound)
        base_name = os.path.splitext(sound_name)[0]
        
        if current_tab == 0:
            suggestion = f"{base_name}_waveform.png"
            title = "Export Waveform"
        else:
            suggestion = f"{base_name}_spectrogram.png"
            title = "Export Spectrogram"
            
        # Ask user for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, title, suggestion, "Images (*.png *.jpg)"
        )
        
        if not file_path:
            return
            
        try:
            # Save the figure
            if current_tab == 0:
                self.waveform_canvas.fig.savefig(file_path, dpi=300, bbox_inches='tight')
            else:
                self.spectrogram_canvas.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                
            QMessageBox.information(self, "Export Complete", 
                                   f"Visualization exported to {file_path}")
                                   
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Error exporting image: {str(e)}")
            
    def show_context_menu(self, position):
        """Show context menu for sound list"""
        items = self.sound_list.selectedItems()
        if not items:
            return
            
        menu = QMenu()
        
        play_action = menu.addAction("Play")
        visualize_action = menu.addAction("Visualize")
        menu.addSeparator()
        remove_action = menu.addAction("Remove")
        
        action = menu.exec_(self.sound_list.mapToGlobal(position))
        
        if action == play_action:
            self.play_sound()
        elif action == visualize_action:
            # Already visualized on selection
            pass
        elif action == remove_action:
            self.remove_selected_sound()
            
    def remove_selected_sound(self):
        """Remove the selected sound file"""
        items = self.sound_list.selectedItems()
        if not items:
            return
            
        sound_file = items[0].text()
        sound_path = os.path.join(self.sounds_dir, sound_file)
        
        # Confirm deletion
        if QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete sound '{sound_file}'?",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
            
        try:
            # Stop playback if this is the current sound
            if self.current_sound == sound_path:
                self.stop_sound()
                self.current_sound = None
                
            # Delete the file
            os.remove(sound_path)
            
            # Remove from list
            row = self.sound_list.row(items[0])
            self.sound_list.takeItem(row)
            
            # Reset UI
            self.sound_info.setText("Select a sound to visualize")
            self.play_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.export_button.setEnabled(False)
            
        except Exception as e:
            QMessageBox.warning(self, "Delete Error", f"Error deleting sound: {str(e)}")