import os
import wave
import tempfile
import random
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import pygame
import time
import contextlib

class SoundEffect:
    """Represents a sound effect that can be applied to a bell sound"""
    
    def __init__(self, name, effect_type, parameters=None):
        self.name = name
        self.type = effect_type  # 'fade', 'echo', 'reverb', 'pitch', 'eq', etc.
        self.parameters = parameters or {}
        
    def to_dict(self):
        """Convert to dictionary for storage"""
        return {
            "name": self.name,
            "type": self.type,
            "parameters": self.parameters
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            name=data["name"],
            effect_type=data["type"],
            parameters=data.get("parameters", {})
        )


class SoundMixer(QObject):
    """Advanced sound mixer for bell sounds with effects and layering"""
    
    # Signals
    mix_completed = pyqtSignal(str)  # Path to mixed sound
    mix_failed = pyqtSignal(str)  # Error message
    
    def __init__(self, sounds_dir="assets/sounds"):
        super().__init__()
        self.sounds_dir = sounds_dir
        
        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    
    def apply_fade(self, samples, fade_in=0.0, fade_out=0.0, sample_rate=44100):
        """Apply fade in/out to sound samples"""
        if fade_in <= 0 and fade_out <= 0:
            return samples
            
        fade_in_samples = int(fade_in * sample_rate)
        fade_out_samples = int(fade_out * sample_rate)
        
        # Create a copy to avoid modifying the original
        result = np.copy(samples)
        
        # Apply fade in
        if fade_in > 0:
            fade_in_curve = np.linspace(0, 1, fade_in_samples)
            result[:fade_in_samples] *= fade_in_curve[:, np.newaxis]
            
        # Apply fade out
        if fade_out > 0:
            fade_out_curve = np.linspace(1, 0, fade_out_samples)
            result[-fade_out_samples:] *= fade_out_curve[:, np.newaxis]
            
        return result
            
    def apply_echo(self, samples, delay=0.3, decay=0.5, sample_rate=44100):
        """Apply echo effect to sound samples"""
        delay_samples = int(delay * sample_rate)
        
        # Create output array (original + echo)
        result = np.copy(samples)
        
        # Add echo
        if delay_samples < len(samples):
            echo = np.copy(samples[:-delay_samples])
            echo = echo * decay
            result[delay_samples:] += echo
            
        return result
            
    def apply_pitch_shift(self, samples, semitones=0):
        """Apply pitch shift to sound samples"""
        if semitones == 0:
            return samples
            
        # Calculate pitch factor (2^(semitones/12))
        factor = 2 ** (semitones / 12)
        
        # Resample using linear interpolation (simplistic approach)
        indices = np.arange(0, len(samples), factor)
        indices = indices.astype(np.int32)
        indices = indices[indices < len(samples)]
        
        return samples[indices]
            
    def apply_effect(self, samples, effect, sample_rate=44100):
        """Apply a sound effect to samples"""
        if effect.type == "fade":
            fade_in = effect.parameters.get("fade_in", 0.0)
            fade_out = effect.parameters.get("fade_out", 0.0)
            return self.apply_fade(samples, fade_in, fade_out, sample_rate)
            
        elif effect.type == "echo":
            delay = effect.parameters.get("delay", 0.3)
            decay = effect.parameters.get("decay", 0.5)
            return self.apply_echo(samples, delay, decay, sample_rate)
            
        elif effect.type == "pitch":
            semitones = effect.parameters.get("semitones", 0)
            return self.apply_pitch_shift(samples, semitones)
            
        # Default: return unmodified samples
        return samples
            
    def create_layered_sound(self, sound_files, volumes=None, output_path=None, effects=None):
        """Mix multiple sounds together with different volumes and effects
        
        Args:
            sound_files: List of sound file paths
            volumes: List of volume percentages (0-100) for each sound
            output_path: Where to save the mixed sound (temp file if None)
            effects: List of SoundEffect objects to apply
            
        Returns:
            str: Path to the mixed sound file
        """
        try:
            # Validate input
            if not sound_files:
                raise ValueError("No sound files provided for mixing")
                
            if volumes is None:
                volumes = [100] * len(sound_files)
                
            if len(volumes) != len(sound_files):
                volumes = volumes + [100] * (len(sound_files) - len(volumes))
                
            # Convert volume percentages to factors (0.0-1.0)
            volume_factors = [v / 100 for v in volumes]
            
            # Ensure files exist and expand relative paths
            full_paths = []
            for sound_file in sound_files:
                if not os.path.isabs(sound_file):
                    sound_file = os.path.join(self.sounds_dir, sound_file)
                if not os.path.exists(sound_file):
                    raise FileNotFoundError(f"Sound file not found: {sound_file}")
                full_paths.append(sound_file)
                
            # Create output path if not provided
            if output_path is None:
                output_path = tempfile.mktemp(suffix=".wav", prefix="bell_mix_")
            elif not os.path.isabs(output_path):
                output_path = os.path.join(self.sounds_dir, output_path)
                
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Read all sound files and determine max length
            sound_data = []
            max_length = 0
            sample_rate = 44100  # Default sample rate
            
            for i, sound_file in enumerate(full_paths):
                # Get sound data as numpy array
                with contextlib.closing(wave.open(sound_file, 'rb')) as wf:
                    sample_rate = wf.getframerate()
                    n_channels = wf.getnchannels()
                    sample_width = wf.getsampwidth()
                    n_frames = wf.getnframes()
                    
                    # Read all frames
                    raw_data = wf.readframes(n_frames)
                    
                    # Convert to numpy array
                    if sample_width == 2:  # 16-bit
                        data = np.frombuffer(raw_data, dtype=np.int16)
                    elif sample_width == 4:  # 32-bit
                        data = np.frombuffer(raw_data, dtype=np.int32)
                    else:
                        data = np.frombuffer(raw_data, dtype=np.uint8)
                        
                    # Reshape if stereo
                    if n_channels == 2:
                        data = data.reshape(-1, 2)
                    else:
                        # Convert mono to stereo
                        data = np.column_stack((data, data))
                        
                    # Apply volume
                    data = data * volume_factors[i]
                    
                    # Apply effects
                    if effects:
                        for effect in effects:
                            data = self.apply_effect(data, effect, sample_rate)
                            
                    # Store data and update max length
                    sound_data.append(data)
                    max_length = max(max_length, len(data))
            
            # Pad shorter sounds to max length
            for i in range(len(sound_data)):
                if len(sound_data[i]) < max_length:
                    padding = np.zeros((max_length - len(sound_data[i]), 2), dtype=sound_data[i].dtype)
                    sound_data[i] = np.vstack((sound_data[i], padding))
            
            # Mix all sounds
            mixed_data = np.zeros((max_length, 2), dtype=np.float32)
            for data in sound_data:
                mixed_data += data.astype(np.float32)
                
            # Normalize to prevent clipping
            max_value = np.max(np.abs(mixed_data))
            if max_value > 0:
                mixed_data = mixed_data * (32767 / max_value)
                
            # Convert back to int16
            mixed_data = mixed_data.astype(np.int16)
            
            # Write to output file
            with contextlib.closing(wave.open(output_path, 'wb')) as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(mixed_data.tobytes())
                
            # Signal completion
            self.mix_completed.emit(output_path)
            
            return output_path
            
        except Exception as e:
            error_message = f"Error mixing sounds: {str(e)}"
            print(error_message)
            self.mix_failed.emit(error_message)
            return None
            
    def create_random_variation(self, sound_file, output_path=None, variation_type="pitch"):
        """Create a random variation of a sound file
        
        Args:
            sound_file: Path to the source sound file
            output_path: Where to save the variation (temp file if None)
            variation_type: Type of variation to apply (pitch, echo, speed)
            
        Returns:
            str: Path to the varied sound file
        """
        try:
            # Determine output path
            if output_path is None:
                output_path = tempfile.mktemp(suffix=".wav", prefix="bell_var_")
            elif not os.path.isabs(output_path):
                output_path = os.path.join(self.sounds_dir, output_path)
                
            # Ensure sound file exists
            if not os.path.isabs(sound_file):
                sound_file = os.path.join(self.sounds_dir, sound_file)
            if not os.path.exists(sound_file):
                raise FileNotFoundError(f"Sound file not found: {sound_file}")
                
            # Create appropriate effect based on variation type
            effects = []
            
            if variation_type == "pitch":
                # Random pitch shift between -2 and +2 semitones
                semitones = random.uniform(-2, 2)
                effects.append(SoundEffect("Random Pitch", "pitch", {"semitones": semitones}))
                
            elif variation_type == "echo":
                # Random echo
                delay = random.uniform(0.1, 0.3)
                decay = random.uniform(0.3, 0.6)
                effects.append(SoundEffect("Random Echo", "echo", {"delay": delay, "decay": decay}))
                
            elif variation_type == "fade":
                # Random fade in/out
                fade_in = random.uniform(0.0, 0.2)
                fade_out = random.uniform(0.0, 0.3)
                effects.append(SoundEffect("Random Fade", "fade", {"fade_in": fade_in, "fade_out": fade_out}))
                
            # Apply the effects
            return self.create_layered_sound([sound_file], [100], output_path, effects)
            
        except Exception as e:
            error_message = f"Error creating sound variation: {str(e)}"
            print(error_message)
            self.mix_failed.emit(error_message)
            return None
            
    def visualize_sound(self, sound_file, output_path=None):
        """Generate a visualization of a sound file as an image
        
        Args:
            sound_file: Path to the sound file
            output_path: Where to save the image (temp file if None)
            
        Returns:
            str: Path to the image file
        """
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            
            # Determine output path
            if output_path is None:
                output_path = tempfile.mktemp(suffix=".png", prefix="bell_viz_")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Ensure sound file exists
            if not os.path.isabs(sound_file):
                sound_file = os.path.join(self.sounds_dir, sound_file)
            if not os.path.exists(sound_file):
                raise FileNotFoundError(f"Sound file not found: {sound_file}")
            
            # Read sound file
            with contextlib.closing(wave.open(sound_file, 'rb')) as wf:
                sample_rate = wf.getframerate()
                n_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                n_frames = wf.getnframes()
                
                # Read all frames
                raw_data = wf.readframes(n_frames)
                
                # Convert to numpy array
                if sample_width == 2:  # 16-bit
                    data = np.frombuffer(raw_data, dtype=np.int16)
                elif sample_width == 4:  # 32-bit
                    data = np.frombuffer(raw_data, dtype=np.int32)
                else:
                    data = np.frombuffer(raw_data, dtype=np.uint8)
                    
                # Take just one channel if stereo
                if n_channels == 2:
                    data = data[::2]  # Take left channel
            
            # Create time array
            time = np.linspace(0, n_frames / sample_rate, num=len(data))
            
            # Create visualization
            plt.figure(figsize=(10, 6))
            
            # Waveform
            plt.subplot(2, 1, 1)
            plt.plot(time, data, color='#00a0ff')
            plt.title('Waveform')
            plt.xlabel('Time (s)')
            plt.ylabel('Amplitude')
            plt.grid(True, alpha=0.3)
            
            # Spectrogram
            plt.subplot(2, 1, 2)
            plt.specgram(data, Fs=sample_rate, cmap='viridis')
            plt.title('Spectrogram')
            plt.xlabel('Time (s)')
            plt.ylabel('Frequency (Hz)')
            plt.colorbar(label='Intensity (dB)')
            
            # Title for entire figure
            plt.suptitle(f"Sound Visualization: {os.path.basename(sound_file)}", fontsize=16)
            
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            plt.savefig(output_path)
            plt.close()
            
            return output_path
            
        except Exception as e:
            error_message = f"Error visualizing sound: {str(e)}"
            print(error_message)
            return None