# [Moku-Go](https://github.com/sealablab/Moku-Go)

The CLI you always wanted

# Usage
## Discover Devices
```bash
moku-go discover
```
This will find all Moku devices on your network and cache their information for future use.

## Connect to a Device
You can connect using either the device's IP address or its name:
```bash
# Using IP address
moku-go connect 10.0.44.219

# Using device name
moku-go connect Lilo
```

## Scope
You can use either IP address or device name:
```bash
# Using IP address
moku-go scope 10.0.44.219

# Using device name
moku-go scope Lilo
```

# With configuration file
moku-go scope 10.0.44.219 --config moku_go/config/scope_config.yaml

# Force connection if device is in use
moku-go scope 10.0.44.219 --force

# Device Name Resolution
The CLI maintains a cache of discovered devices in `~/.moku-go/device_cache.json`. This allows you to:
- Use device names instead of IP addresses in commands
- Avoid running discovery every time you want to connect

If the cache becomes invalid, you'll be prompted to run `moku-go discover` again.

# Installation
We use [uv](https://docs.astral.sh/uv/) for project management, so
```
git clone git@github.com:sealablab/Moku-Go.git
cd  Moku-Go
johnycsh@DRP-e1 Moku-Go % uv sync
```

# Running
```
johnycsh@DRP-e1 Moku-Go % uv run hello.py
johnycsh@DRP-e1 Moku-Go % uv run osc.py
```

# Environment Variables

## Official Moku Environment Variables

- `MOKU_IP`: The IP address of your Moku device. This can be used instead of providing the IP address as a command-line argument.
  ```bash
  export MOKU_IP=10.0.44.219
  ```

- `MOKU_DATA_PATH`: Path to the directory containing Moku bitstreams. Required for instrument functionality.
  ```bash
  export MOKU_DATA_PATH=./mokudatadir
  ```

## Custom Environment Variables

These variables allow fine-tuning of the connection behavior:

- `MOKU_FORCE_CONNECT`: Force connection even if device is in use (default: true)
  ```bash
  export MOKU_FORCE_CONNECT=true
  ```

- `MOKU_IGNORE_BUSY`: Ignore device busy state (default: true)
  ```bash
  export MOKU_IGNORE_BUSY=true
  ```

- `MOKU_PERSIST_STATE`: Maintain device state between connections (default: true)
  ```bash
  export MOKU_PERSIST_STATE=true
  ```

- `MOKU_CONNECT_TIMEOUT`: Connection timeout in seconds (default: 10)
  ```bash
  export MOKU_CONNECT_TIMEOUT=10
  ```

- `MOKU_READ_TIMEOUT`: Read timeout in seconds (default: 10)
  ```bash
  export MOKU_READ_TIMEOUT=10
  ```

# Setting up Moku Bitstreams

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

# Debugging:
I get the following error
 ```  File "osc.py"
       data = i.get_data()
AttributeError: 'NoneType' object has no attribute 'get_data'
```
Moku-Go was unable to locate your upstream bitstreams. 
Check your `MOKU_DATA_PATH` Env var, and try again.
