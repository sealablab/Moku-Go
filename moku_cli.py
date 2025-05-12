#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from loguru import logger
from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange
from moku import Moku
import sys

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

class MokuDevice:
    def __init__(self, ip: str = None):
        self.ip = ip
        self.device = None

    def connect(self, force: bool = False) -> bool:
        """Connect to the Moku device"""
        try:
            self.device = Moku(ip=self.ip, force_connect=force)
            logger.info(f"Successfully connected to Moku device at {self.ip}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            return False

    def disconnect(self):
        """Disconnect from the Moku device"""
        if self.device:
            try:
                self.device.relinquish_ownership()
                logger.info("Disconnected from Moku device")
            except Exception as e:
                logger.error(f"Error disconnecting from device: {e}")

def discover_devices() -> list:
    """Discover Moku devices on the network using zeroconf"""
    devices = []
    zc = Zeroconf()
    
    def on_service_state_change(zeroconf, service_type, name, state_change):
        if state_change == ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                devices.append({
                    'name': name,
                    'ip': '.'.join(str(x) for x in info.parsed_addresses()[0]),
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
    ip: str = typer.Argument(..., help="IP address of the Moku device"),
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

def main():
    setup_logging()
    app()

if __name__ == "__main__":
    main() 