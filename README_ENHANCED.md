# DPMMV Bells System (ENHANCED)

A feature-rich, dark-themed, responsive Python desktop GUI application for managing, playing, and tracking school or general-purpose alarms with an extremely polished UI and now with **over 50+ advanced features**.

## 🚀 NEW ADVANCED FEATURES

### 📊 Advanced Analytics Engine
- Real-time bell usage statistics with interactive dashboards
- Activity heatmaps showing bell patterns across days and hours
- Comprehensive reporting with exportable HTML reports
- Category distribution analytics with visual graphs
- Performance metrics and system health monitoring

### 🔊 Sound Mixing & Audio Labs
- Layer multiple sounds to create custom bell tones
- Apply audio effects including fade, echo, and pitch shifting
- Visual waveform and spectrogram displays for all sounds
- Create random sound variations for more natural alerts
- Export mixed sounds to use across the system

### 🏫 Multi-Zone Bell Control
- Configure different physical zones/rooms/areas
- Custom volume settings per zone
- Zone-specific bell schedules and restrictions
- Visual zone status monitoring
- Zone grouping and mass-control capabilities

### 📝 Examination Mode
- Dedicated examination timer with configurable durations
- Reading time support with automatic transitions
- Warning bells at configurable intervals
- Visual countdown with color-coded progress bars
- Full-screen examination display mode

### 🔄 Smart Bell Enhancement
- Bell sequence optimization to avoid overlaps
- Automatic volume adjustment based on time of day
- Sound variation to prevent "alert fatigue"
- Intelligent recovery for missed bells
- Schedule conflict detection and resolution

## Original Features

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

## Enhanced File Structure

```
/DPMMV_Bells_System
│
├── main.py
├── /core
│   ├── scheduler.py
│   ├── bell_engine.py
│   ├── bell_player.py
│   ├── bell_loader.py
│   ├── analytics_engine.py    [NEW]
│   ├── multi_zone_controller.py [NEW]
│   ├── sound_mixer.py         [NEW]
│   └── auto_restore.py
│
├── /ui
│   ├── splash_screen.py
│   ├── main_window.py
│   ├── bell_editor.py
│   ├── analytics_dashboard.py [NEW]
│   ├── zone_manager.py        [NEW]
│   ├── sound_mixer_ui.py      [NEW]
│   ├── sound_visualizer.py    [NEW]
│   ├── examination_mode.py    [NEW]
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
│   ├── zones.json           [NEW]
│   ├── analytics_data.json  [NEW]
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