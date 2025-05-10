import os
import numpy as np
import scipy.io.wavfile
import wave
import struct

def create_bell_sound(output_path, duration=2.0, sample_rate=44100):
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create a simple bell-like sound
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Use a combination of frequencies for a bell-like sound
    primary_freq = 440.0  # A4 note
    f1, f2, f3 = primary_freq, primary_freq * 2, primary_freq * 3
    
    # Create a decaying envelope
    envelope = np.exp(-t * 3)
    
    # Combine frequencies with different weights
    signal = 0.7 * np.sin(2 * np.pi * f1 * t) + 0.2 * np.sin(2 * np.pi * f2 * t) + 0.1 * np.sin(2 * np.pi * f3 * t)
    signal = signal * envelope
    
    # Normalize to 16-bit range
    signal = signal * 32767 / np.max(np.abs(signal))
    signal = signal.astype(np.int16)
    
    # Write WAV file
    wav_path = output_path.replace('.mp3', '.wav')
    scipy.io.wavfile.write(wav_path, sample_rate, signal)
    
    print(f"Created default bell sound: {wav_path}")
    
    # Attempt to convert to MP3 if needed
    if output_path.endswith('.mp3'):
        try:
            import pydub
            from pydub import AudioSegment
            sound = AudioSegment.from_wav(wav_path)
            sound.export(output_path, format="mp3")
            print(f"Converted to MP3: {output_path}")
        except ImportError:
            print("pydub not available, keeping WAV format")
        except Exception as e:
            print(f"Error converting to MP3: {e}")

if __name__ == "__main__":
    output_path = 'assets/sounds/default.mp3'
    try:
        import scipy.io.wavfile
        create_bell_sound(output_path)
    except ImportError:
        print("scipy not available, using alternative method")
        
        # Alternative method using wave module
        try:
            sample_rate = 44100
            duration = 2  # seconds
            frequency = 440  # Hz
            
            # Create the WAV file
            wav_path = output_path.replace(".mp3", ".wav")
            os.makedirs(os.path.dirname(wav_path), exist_ok=True)
            
            with wave.open(wav_path, 'w') as wav_file:
                wav_file.setparams((1, 2, sample_rate, 0, 'NONE', 'not compressed'))
                
                # Generate bell-like sound samples
                samples = []
                for i in range(int(duration * sample_rate)):
                    t = i / sample_rate
                    # Decaying sine wave
                    decay = np.exp(-t * 3)
                    value = int(32767 * decay * 0.5 * (
                        0.6 * np.sin(2 * np.pi * 440 * t) +
                        0.3 * np.sin(2 * np.pi * 880 * t) +
                        0.1 * np.sin(2 * np.pi * 1760 * t)
                    ))
                    packed_value = struct.pack('h', value)
                    samples.append(packed_value)
                
                # Write samples to file
                wav_file.writeframes(b''.join(samples))
            
            print(f"Created default bell sound: {wav_path}")
        except Exception as e:
            print(f"Error creating sound: {e}")
            
            # Fallback to pygame if all else fails
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), "assets/sounds/default.wav"))
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Could not create default sound: {e}")