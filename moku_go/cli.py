#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from loguru import logger
from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange
import sys
import yaml
from pathlib import Path
import os
import logging
import json
import datetime

from .device import MokuDevice
from .osc import MokuOscilloscope

# Initialize Typer app
app = typer.Typer(
    name="moku-go",
    help="CLI interface for Liquid Instruments Moku-Go device",
    add_completion=False,
    invoke_without_command=True,
)

# Initialize Rich console
console = Console()

# Cache file path
CACHE_FILE = Path.home() / ".moku-go" / "device_cache.json"

# Cache for discovered devices, keyed by IP
known_devices = {}

def load_cache():
    """Load the device cache from disk"""
    global known_devices
    try:
        if not CACHE_FILE.exists():
            return
        with open(CACHE_FILE) as f:
            known_devices = json.load(f)
    except Exception as e:
        logger.warning(f"Could not load device cache: {e}")
        try:
            CACHE_FILE.unlink()
        except Exception:
            pass
        console.print("[yellow]Device cache was invalid. Please run 'moku-go discover' to find devices.[/yellow]")

def save_cache():
    """Save the device cache to disk"""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump(known_devices, f)
    except Exception as e:
        logger.warning(f"Could not save device cache: {e}")

# Root Log Redirection
# -------------------
# This block redirects logs from Python's standard logging module (used by the 'moku' module)
# to Loguru. It does this by:
# 1. Defining a custom logging handler (InterceptHandler) that captures log records
#    from the root logger.
# 2. For each log record, it converts the log level to a Loguru level and uses
#    Loguru's logger.opt() to log the message with the correct depth and exception info.
# 3. Configuring the root logger to use this handler, ensuring that any logs from
#    the 'moku' module (or any other module using Python's logging) are captured
#    and formatted by Loguru.
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0)

def humanize_time_ago(dt: datetime.datetime) -> str:
    now = datetime.datetime.utcnow()
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """CLI interface for Liquid Instruments Moku-Go device"""
    # Set up logging
    loglevel = os.environ.get("MOKU_LOGLEVEL", "WARNING")
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=loglevel.upper(),
        colorize=True,
    )
    logger.debug(f"Loguru configured with level: {loglevel.upper()}")
    
    # Load device cache
    load_cache()
    
    # Show help if no command provided
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        # Print cached devices summary
        if known_devices:
            table = Table(show_header=True, header_style="bold yellow")
            table.add_column("Name")
            table.add_column("IP Address")
            table.add_column("Port")
            table.add_column("Serial Number")
            table.add_column("Last Seen")
            for device in known_devices.values():
                name = device.get('canonical_name') or 'N/A'
                ip = device.get('ip', 'N/A')
                port = str(device.get('port', 'N/A'))
                serial = device.get('serial_number', 'N/A')
                last_seen = device.get('last_seen')
                if last_seen:
                    try:
                        dt = datetime.datetime.fromisoformat(last_seen)
                        last_seen_str = humanize_time_ago(dt)
                    except Exception:
                        last_seen_str = last_seen
                else:
                    last_seen_str = 'N/A'
                table.add_row(name, ip, port, serial, last_seen_str)
            console.print("\n[bold]Device Cache:[/bold]")
            console.print(table)
        raise typer.Exit()

def discover_devices() -> list:
    """Discover Moku devices on the network using zeroconf"""
    devices = []
    zc = Zeroconf()
    
    def on_service_state_change(zeroconf, service_type, name, state_change):
        if state_change == ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                addresses = info.parsed_addresses()
                ipv4_addresses = [addr for addr in addresses if ':' not in addr]
                ip = ipv4_addresses[0] if ipv4_addresses else addresses[0]
                now = datetime.datetime.utcnow().isoformat()
                device_info = {
                    'zeroconf_name': name,
                    'ip': ip,
                    'port': info.port,
                    'canonical_name': None,  # Will be set after successful connect
                    'last_seen': now
                }
                devices.append(device_info)
                # Cache is keyed by IP only
                known_devices[ip] = device_info

    browser = ServiceBrowser(zc, "_moku._tcp.local.", handlers=[on_service_state_change])
    import time
    time.sleep(2)
    zc.close()
    save_cache()
    return devices

@app.command()
def discover(
    timeout: int = typer.Option(2, help="Discovery timeout in seconds", metavar="SECONDS"),
):
    """Discover Moku devices on the network"""
    console.print("[bold blue]Discovering Moku devices...[/bold blue]")
    
    # Clear the cache before new discovery
    known_devices.clear()
    devices = discover_devices()
    
    if not devices:
        console.print("[yellow]No Moku devices found on the network[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("IP Address")
    table.add_column("Port")
    table.add_column("Serial Number")

    for device in devices:
        # Connect to the device to retrieve metadata
        moku_device = MokuDevice(ip=device['ip'])
        if moku_device.connect():
            metadata = moku_device.get_metadata()
            canonical_name = metadata["name"]
            serial_number = metadata["serial_number"]
            now = datetime.datetime.utcnow().isoformat()
            # Update cache with metadata
            known_devices[device['ip']].update({
                'canonical_name': canonical_name,
                'serial_number': serial_number,
                'last_seen': now
            })
        else:
            canonical_name = "N/A"
            serial_number = "N/A"
        moku_device.disconnect()

        table.add_row(
            canonical_name,
            device['ip'],
            str(device['port']),
            serial_number
        )

    # Save cache after updating with metadata
    save_cache()
    console.print(table)

@app.command()
def connect(
    identifier: str = typer.Argument(
        ..., 
        help="IP address or name of the Moku device (can also be set via MOKU_IP env var)",
        envvar="MOKU_IP",
        metavar="IP_OR_NAME"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force connection even if device is in use"),
):
    """Connect to a Moku device"""
    ip = None
    if all(c.isdigit() or c == '.' for c in identifier):
        ip = identifier
    else:
        # Search cache for a matching name
        for cached_ip, device_info in known_devices.items():
            if device_info.get('canonical_name', '').lower() == identifier.lower():
                ip = cached_ip
                break
        if not ip:
            raise typer.BadParameter(f"Device '{identifier}' not found. Please run 'moku-go discover' first.")

    console.print(f"[bold blue]Connecting to Moku device at {ip}...[/bold blue]")
    device = MokuDevice(ip=ip)
    if device.connect(force=force):
        # Update cache with canonical name after successful connect
        now = datetime.datetime.utcnow().isoformat()
        known_devices[ip]['canonical_name'] = device.name
        known_devices[ip]['last_seen'] = now
        save_cache()
        console.print("[green]Successfully connected to device[/green]")
    else:
        console.print("[red]Failed to connect to device[/red]")
        raise typer.Exit(1)

@app.command()
def scope(
    identifier: str = typer.Argument(
        ..., 
        help="IP address or name of the Moku device (can also be set via MOKU_IP env var)",
        envvar="MOKU_IP",
        metavar="IP_OR_NAME"
    ),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to YAML configuration file", metavar="FILE"),
    force: bool = typer.Option(False, "--force", "-f", help="Force connection even if device is in use"),
):
    """Connect to and configure the oscilloscope instrument"""
    ip = None
    if all(c.isdigit() or c == '.' for c in identifier):
        ip = identifier
    else:
        # Search cache for a matching name
        for cached_ip, device_info in known_devices.items():
            if device_info.get('canonical_name', '').lower() == identifier.lower():
                ip = cached_ip
                break
        if not ip:
            raise typer.BadParameter(f"Device '{identifier}' not found. Please run 'moku-go discover' first.")

    console.print(f"[bold blue]Connecting to oscilloscope at {ip}...[/bold blue]")
    scope = MokuOscilloscope(ip=ip, force_connect=force)
    if not scope.connect():
        console.print("[red]Failed to connect to oscilloscope[/red]")
        raise typer.Exit(1)
    
    # Load and apply configuration if provided
    if config_file:
        try:
            config_path = Path(config_file)
            with open(config_path) as f:
                scope_config = yaml.safe_load(f)
            if scope.configure(scope_config):
                console.print("[green]Successfully configured oscilloscope[/green]")
            else:
                console.print("[red]Failed to configure oscilloscope[/red]")
                raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error loading configuration: {e}[/red]")
            logger.exception("Error loading configuration file")
            raise typer.Exit(1)
    
    try:
        data = scope.get_data()
        if data:
            console.print("[green]Successfully captured data[/green]")
        else:
            console.print("[red]Failed to capture data[/red]")
    finally:
        scope.disconnect()

@app.command()
def mim(
    identifier: str = typer.Argument(
        ..., 
        help="IP address or name of the Moku device (can also be set via MOKU_IP env var)",
        envvar="MOKU_IP",
        metavar="IP_OR_NAME"
    ),
    bitstream: str = typer.Option(
        ..., 
        "--bitstream", 
        "-b",
        help="Path to bitstream .tar file",
        metavar="FILE"
    ),
    slot: int = typer.Option(
        2, 
        "--slot", 
        "-s",
        help="Slot number for the bitstream (1 or 2)",
        metavar="SLOT"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force connection even if device is in use"),
):
    """Load a bitstream into multi-instrument mode"""
    
    # Validate slot number
    if slot not in [1, 2]:
        raise typer.BadParameter("Slot must be 1 or 2")
    
    # Validate bitstream file exists
    bitstream_path = Path(bitstream)
    if not bitstream_path.exists():
        raise typer.BadParameter(f"Bitstream file not found: {bitstream}")
    
    # Resolve device IP
    ip = None
    if all(c.isdigit() or c == '.' for c in identifier):
        ip = identifier
    else:
        # Search cache for a matching name
        for cached_ip, device_info in known_devices.items():
            if device_info.get('canonical_name', '').lower() == identifier.lower():
                ip = cached_ip
                break
        if not ip:
            raise typer.BadParameter(f"Device '{identifier}' not found. Please run 'moku-go discover' first.")
    
    console.print(f"[bold blue]Loading bitstream into multi-instrument mode at {ip}...[/bold blue]")
    
    try:
        # Import here to avoid dependency issues if moku package not installed
        from moku.instruments import MultiInstrument, CloudCompile
        
        # Connect to device in multi-instrument mode
        mim = MultiInstrument(ip, platform_id=2, force_connect=force)
        
        # Load bitstream into specified slot
        mcc = mim.set_instrument(slot, CloudCompile, bitstream=str(bitstream_path))
        
        console.print(f"[green]Successfully loaded bitstream into slot {slot}[/green]")
        console.print(f"[green]Bitstream: {bitstream_path.name}[/green]")
        
        # Get device info
        try:
            device_info = mim.describe()
            console.print(f"[green]Device: {device_info.get('hardware', 'Unknown')}[/green]")
            console.print(f"[green]Firmware: {device_info.get('firmware', 'Unknown')}[/green]")
        except Exception as e:
            logger.debug(f"Could not retrieve device info: {e}")
        
        # Keep connection open for user to interact with
        console.print("[yellow]Multi-instrument mode is now active. Press Ctrl+C to disconnect.[/yellow]")
        
        try:
            # Keep the connection alive
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Disconnecting...[/yellow]")
        finally:
            mim.relinquish_ownership()
            console.print("[green]Disconnected from device[/green]")
            
    except ImportError:
        console.print("[red]Error: moku package not found. Please install it with: pip install moku[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Failed to load bitstream: {e}[/red]")
        logger.exception("Error loading bitstream")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
