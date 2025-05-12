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

from .device import MokuDevice
from .osc import MokuOscilloscope

# Initialize Typer app
app = typer.Typer(
    name="moku-go",
    help="CLI interface for Liquid Instruments Moku-Go device",
    add_completion=False,
)

# Initialize Rich console
console = Console()

def setup_logging():
    """Configure logging with loguru"""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )

def discover_devices() -> list:
    """Discover Moku devices on the network using zeroconf"""
    devices = []
    zc = Zeroconf()
    
    def on_service_state_change(zeroconf, service_type, name, state_change):
        if state_change == ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                # Get all addresses
                addresses = info.parsed_addresses()
                # Prefer IPv4 addresses
                ipv4_addresses = [addr for addr in addresses if ':' not in addr]
                # Use first IPv4 address if available, otherwise fall back to first address
                ip = ipv4_addresses[0] if ipv4_addresses else addresses[0]
                
                devices.append({
                    'name': name,
                    'ip': ip,
                    'port': info.port
                })

    browser = ServiceBrowser(zc, "_moku._tcp.local.", handlers=[on_service_state_change])
    # Wait for discovery (you might want to adjust this timeout)
    import time
    time.sleep(2)
    zc.close()
    return devices

@app.command()
def discover(
    timeout: int = typer.Option(2, help="Discovery timeout in seconds")
):
    """Discover Moku devices on the network"""
    console.print("[bold blue]Discovering Moku devices...[/bold blue]")
    
    devices = discover_devices()
    
    if not devices:
        console.print("[yellow]No Moku devices found on the network[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("IP Address")
    table.add_column("Port")

    for device in devices:
        table.add_row(
            device['name'],
            device['ip'],
            str(device['port'])
        )

    console.print(table)

@app.command()
def connect(
    ip: str = typer.Argument(
        ..., 
        help="IP address of the Moku device (can also be set via MOKU_IP env var)",
        envvar="MOKU_IP"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Force connection even if device is in use")
):
    """Connect to a Moku device"""
    console.print(f"[bold blue]Connecting to Moku device at {ip}...[/bold blue]")
    
    device = MokuDevice(ip=ip)
    if device.connect(force=force):
        console.print("[green]Successfully connected to device[/green]")
    else:
        console.print("[red]Failed to connect to device[/red]")
        raise typer.Exit(1)

@app.command()
def scope(
    ip: str = typer.Argument(
        ..., 
        help="IP address of the Moku device (can also be set via MOKU_IP env var)",
        envvar="MOKU_IP"
    ),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Path to YAML configuration file"),
    force: bool = typer.Option(False, "--force", "-f", help="Force connection even if device is in use")
):
    """Connect to and configure the oscilloscope instrument"""
    console.print(f"[bold blue]Connecting to oscilloscope at {ip}...[/bold blue]")
    
    # Create and connect oscilloscope
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
            raise typer.Exit(1)
    
    try:
        # Get and display data
        data = scope.get_data()
        if data:
            console.print("[green]Successfully captured data[/green]")
            # TODO: Add data visualization or export functionality
        else:
            console.print("[red]Failed to capture data[/red]")
    finally:
        scope.disconnect()

def main():
    setup_logging()
    app()

if __name__ == "__main__":
    main()
