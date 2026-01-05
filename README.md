# Simple Text Expander

A cross-platform text expansion application with a modern dark-themed GUI built with CustomTkinter.

## Features

- **Global Keyboard Monitoring**: Detects prefix triggers across all applications
- **Application Whitelisting**: Run globally or restrict to specific applications
- **Grouped Expansions**: Organize expansions into groups for better management
- **Custom Prefixes**: Use any prefix format (e.g., `/info`, `.info`, `$info`)
- **Flexible Triggers**: Immediate expansion or configurable delay
- **JSON Import/Export**: Easy backup and sharing of expansions
- **Automatic Updates**: Check for updates from GitHub releases
- **Dark Theme**: Modern, easy-on-the-eyes interface

## Installation

### Windows

Download the latest installer from the [Releases](https://github.com/yourusername/simple_text_expander/releases) page and run the setup executable.

### macOS

Download the DMG or ZIP file from the [Releases](https://github.com/yourusername/simple_text_expander/releases) page.

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/simple_text_expander.git
cd simple_text_expander
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python src/main.py
```

## Usage

1. **Start Monitoring**: Click "Start Monitoring" to begin detecting expansions
2. **Create Groups**: Add groups to organize your expansions
3. **Add Expansions**: 
   - Select a group
   - Click "Add Expansion"
   - Enter a prefix (e.g., `/info`)
   - Enter the expanded text
   - Configure trigger options (immediate or delayed)
4. **Configure Whitelist**: 
   - Go to Settings tab
   - Enable whitelist to restrict to specific applications
   - Add applications by process name or window title
5. **Export/Import**: Use the Export/Import buttons to backup or share your expansions

## Data Storage

All expansion data is stored in:
- **Windows**: `Documents/SimpleTextExpander/data.json`
- **macOS**: `Documents/SimpleTextExpander/data.json`

This makes it easy to backup your expansions by simply copying this file.

## Requirements

- Python 3.11+
- Windows 10+ or macOS 10.13+

## Dependencies

- customtkinter >= 5.2.0
- Pillow >= 10.0.0
- pynput >= 1.7.6
- pywin32 >= 306 (Windows only)
- psutil >= 5.9.0
- requests >= 2.31.0
- packaging >= 23.0

## Building

### Windows

```bash
pyinstaller build.spec
```

### macOS

```bash
pyinstaller build.spec
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

