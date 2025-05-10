import os
import pygame
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer

class BellPlayer(QObject):
    """
    Handles playing bell sounds with various features:
    - Custom sound files
    - Volume control
    - Repeat functionality
    - Text-to-speech integration
    """
    
    # Define signals
    playback_started = pyqtSignal(str)  # Bell name
    playback_stopped = pyqtSignal(str)  # Bell name
    playback_error = pyqtSignal(str, str)  # Bell name, error message
    
    def __init__(self, sounds_dir="assets/sounds"):
        super().__init__()
        self.sounds_dir = sounds_dir
        self.current_bell = None
        self.playing = False
        self.stop_flag = False
        self.play_thread = None
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Make sure default sounds directory exists
        os.makedirs(self.sounds_dir, exist_ok=True)
        
        # Create a default sound if none exists
        default_sound = os.path.join(self.sounds_dir, "default.mp3")
        if not os.path.exists(default_sound):
            self.generate_default_sound(default_sound)
    
    def generate_default_sound(self, path):
        """Generate a simple beep sound as default using pygame"""
        try:
            import wave
            import struct
            
            # Create a simple bell-like sound
            sample_rate = 44100
            duration = 2  # seconds
            frequency = 440  # Hz
            
            # Create the WAV file
            with wave.open(path.replace(".mp3", ".wav"), 'w') as wav_file:
                wav_file.setparams((1, 2, sample_rate, 0, 'NONE', 'not compressed'))
                
                # Generate bell-like sound samples
                samples = []
                for i in range(int(duration * sample_rate)):
                    t = i / sample_rate
                    # Decaying sine wave
                    value = int(32767 * 0.5 * (
                        0.6 * (0.5 + 0.5 * (-t/2).exp()) * (2 * 3.14159 * 440 * t).sin() +
                        0.3 * (0.5 + 0.5 * (-t/2).exp()) * (2 * 3.14159 * 880 * t).sin() +
                        0.1 * (0.5 + 0.5 * (-t/2).exp()) * (2 * 3.14159 * 1760 * t).sin()
                    ))
                    packed_value = struct.pack('h', value)
                    samples.append(packed_value)
                
                # Write samples to file
                wav_file.writeframes(b''.join(samples))
            
            print(f"Created default bell sound: {path}")
        except Exception as e:
            print(f"Failed to create default sound: {e}")
            # If the above fails, create a very simple sound
            pygame.mixer.Sound.play()
            pygame.sndarray.make_sound(
                pygame.sndarray.array(pygame.mixer.Sound.play())
            ).write_wav(path.replace(".mp3", ".wav"))
    
    def play_bell(self, bell):
        """Play a bell based on its settings"""
        if self.playing:
            self.stop_playback()
        
        self.current_bell = bell
        self.stop_flag = False
        
        # Start playback in a separate thread
        self.play_thread = threading.Thread(target=self._play_bell_thread, args=(bell,))
        self.play_thread.daemon = True
        self.play_thread.start()
    
    def _play_bell_thread(self, bell):
        """Thread function for playing a bell sound"""
        try:
            self.playing = True
            self.playback_started.emit(bell.name)
            
            # Determine sound file path
            sound_path = os.path.join(self.sounds_dir, bell.sound)
            if not os.path.exists(sound_path):
                sound_path = os.path.join(self.sounds_dir, "default.mp3")
                if not os.path.exists(sound_path):
                    # If no default sound, use the one from pygame
                    print(f"No sound file found for bell: {bell.name}")
                    pygame.mixer.music.load(pygame.mixer.Sound())
                else:
                    pygame.mixer.music.load(sound_path)
            else:
                pygame.mixer.music.load(sound_path)
            
            # Set volume (0.0 to 1.0)
            volume = bell.volume / 100
            pygame.mixer.music.set_volume(volume)
            
            # Play text-to-speech message if enabled
            if bell.tts_message and not bell.silent:
                self._play_tts(bell.tts_message)
            
            # Play the sound if not silent
            if not bell.silent:
                pygame.mixer.music.play()
                
                # If repeat is enabled, loop until stopped
                if bell.repeat:
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    
                    # Wait until stop flag is set
                    while pygame.mixer.music.get_busy() and not self.stop_flag:
                        time.sleep(0.1)
                else:
                    # Wait for sound to finish
                    while pygame.mixer.music.get_busy() and not self.stop_flag:
                        time.sleep(0.1)
            
            self.playing = False
            self.playback_stopped.emit(bell.name)
            
        except Exception as e:
            self.playing = False
            error_msg = str(e)
            print(f"Error playing bell sound: {error_msg}")
            self.playback_error.emit(bell.name, error_msg)
    
    def _play_tts(self, message):
        """Play text-to-speech message"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(message)
            engine.runAndWait()
        except ImportError:
            print("pyttsx3 is not installed. TTS is not available.")
        except Exception as e:
            print(f"Error playing TTS: {e}")
    
    def stop_playback(self):
        """Stop current playback"""
        if self.playing:
            self.stop_flag = True
            pygame.mixer.music.stop()
            
            # Wait for play thread to finish
            if self.play_thread and self.play_thread.is_alive():
                self.play_thread.join(1)
                
            self.playing = False
    
    def set_volume(self, volume):
        """Set global volume (0-100)"""
        pygame.mixer.music.set_volume(volume / 100)
    
    def test_sound(self, sound_file, volume=100):
        """Test a specific sound file"""
        sound_path = os.path.join(self.sounds_dir, sound_file)
        if os.path.exists(sound_path):
            try:
                # Stop any current playback
                if self.playing:
                    self.stop_playback()
                
                # Load and play the test sound
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.set_volume(volume / 100)
                pygame.mixer.music.play()
                
                # Return True if successful
                return True
            except Exception as e:
                print(f"Error testing sound: {e}")
                return False
        else:
            print(f"Sound file not found: {sound_path}")
            return False