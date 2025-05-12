# [Moku-Go](https://github.com/sealablab/Moku-Go)


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![CLI Tool](https://img.shields.io/badge/CLI-Tool-green.svg)](https://github.com/sealablab/Moku-Go)

> The CLI you always wanted 🚀

[![asciicast](https://asciinema.org/a/ktQVg6EboUtowrreHyv1I8SeL.svg?poster=npt:4.0)](https://asciinema.org/a/ktQVg6EboUtowrreHyv1I8SeL)

```bash
$ moku-go
 Usage: moku-go [OPTIONS] COMMAND [ARGS]...                                           
 CLI interface for Liquid Instruments Moku-Go device                                  
                                                                                      
╭─ Options ──────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                        │
╰────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────╮
│ connect      Connect to a Moku device                                              │
│ discover     Discover Moku devices on the network                                  │
│ scope        Connect to and configure the oscilloscope instrument                  │
╰────────────────────────────────────────────────────────────────────────────────────╯

Device Cache:
┏━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Name   ┃ IP Address  ┃ Port  ┃ Serial Number ┃ Last Seen     ┃
┡━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ Lilo   │ 10.0.44.219 │ 27181 │ 007998        │ 8 minutes ago │
│ Stitch │ 10.0.45.61  │ 27181 │ 005628        │ 8 minutes ago │
└────────┴─────────────┴───────┴───────────────┴───────────────┘
```

## 📋 Table of Contents
- [CLI Interface](#cli-interface)
- [Usage](#usage)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Setting up Moku Bitstreams](#setting-up-moku-bitstreams)
- [Debugging](#debugging)


## 🚀 Usage

### 🔍 Discover Devices
```bash
moku-go discover
```
This will find all Moku devices on your network and cache their information for future use.

### 🔌 Connect to a Device
You can connect using either the device's IP address or its name:
```bash
# Using IP address
moku-go connect 10.0.44.219

# Using device name
moku-go connect Lilo
```

### 📊 Scope
You can use either IP address or device name:
```bash
# Using IP address
moku-go scope 10.0.44.219

# Using device name
moku-go scope Lilo
```

#### Advanced Options
```bash
# With configuration file
moku-go scope 10.0.44.219 --config moku_go/config/scope_config.yaml

# Force connection if device is in use
moku-go scope 10.0.44.219 --force
```

### 💾 Device Name Resolution
The CLI maintains a cache of discovered devices in `~/.moku-go/device_cache.json`. This allows you to:
- Use device names instead of IP addresses in commands
- Avoid running discovery every time you want to connect

If the cache becomes invalid, you'll be prompted to run `moku-go discover` again.

## 💻 Installation
We use [uv](https://docs.astral.sh/uv/) for project management:
```bash
git clone git@github.com:sealablab/Moku-Go.git
cd Moku-Go
uv sync
```

## 🏃‍♂️ Running
```bash
uv run hello.py
uv run osc.py
```

## ⚙️ Environment Variables

### Official Moku Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MOKU_IP` | IP address of your Moku device | `export MOKU_IP=10.0.44.219` |
| `MOKU_DATA_PATH` | Path to Moku bitstreams directory | `export MOKU_DATA_PATH=./mokudatadir` |

### Custom Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `MOKU_FORCE_CONNECT` | Force connection if device is in use | true | `export MOKU_FORCE_CONNECT=true` |
| `MOKU_IGNORE_BUSY` | Ignore device busy state | true | `export MOKU_IGNORE_BUSY=true` |
| `MOKU_PERSIST_STATE` | Maintain device state between connections | true | `export MOKU_PERSIST_STATE=true` |
| `MOKU_CONNECT_TIMEOUT` | Connection timeout in seconds | 10 | `export MOKU_CONNECT_TIMEOUT=10` |
| `MOKU_READ_TIMEOUT` | Read timeout in seconds | 10 | `export MOKU_READ_TIMEOUT=10` |

## 📦 Setting up Moku Bitstreams

1. Create a directory for the bitstreams:
   ```bash
   mkdir ./mokudatadir
   ```

2. Move the bitstream archive into the directory:
   ```bash
   mv mokudata-601.tar ./mokudatadir/
   ```

3. Set the environment variable to point to this directory:
   ```bash
   export MOKU_DATA_PATH=./mokudatadir
   ```

## 🐛 Debugging

### Common Error
If you see this error:
```python
File "osc.py"
data = i.get_data()
AttributeError: 'NoneType' object has no attribute 'get_data'
```

**Solution**: Moku-Go was unable to locate your upstream bitstreams. 
Check your `MOKU_DATA_PATH` Env var, and try again.
