# DPMMV Bells System

A feature-rich, dark-themed, responsive Python desktop GUI application for managing, playing, and tracking school or general-purpose alarms with an extremely polished UI and over 40+ advanced features.

## Features

- 🧊 Glassmorphism & neon-themed UI
- 🎆 Custom Loader Splash Screen on start
- 🖥️ Draggable borderless window with custom minimize/maximize
- 🔦 Tray support (hide to system tray, continue playing sounds)
- 🌗 Automatic light/dark theme based on time
- ✅ Unlimited Bells
- 🗓️ Recurring Bells – daily, custom weekdays, monthly, yearly
- 🧠 Smart Schedule Analyzer
- 🕘 Missed Bell Recovery
- And many more...

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DPMMV_Bells_System.git
cd DPMMV_Bells_System
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

1. Launch the application
2. Add bells using the "Add Bell" button
3. Configure bell properties such as name, time, sound, etc.
4. The system will automatically play bells at their scheduled times
5. Use the system tray icon to hide the application while keeping it running

## File Structure

```
/DPMMV_Bells_System
│
├── main.py
├── /core
│   ├── scheduler.py
│   ├── bell_engine.py
│   ├── bell_player.py
│   ├── bell_loader.py
│   └── auto_restore.py
│
├── /ui
│   ├── splash_screen.py
│   ├── main_window.py
│   ├── bell_editor.py
│   ├── timeline.py
│   └── tray_handler.py
│
├── /assets
│   ├── icons/
│   ├── sounds/
│   └── themes/
│
├── /data
│   ├── bells.json
│   ├── user_config.json
│   └── logs.csv
│
└── /utils
    ├── time_utils.py
    ├── tts.py
    └── sound_utils.py
```

## License

[MIT License](LICENSE)

## Credits

Created by DPMMV Team