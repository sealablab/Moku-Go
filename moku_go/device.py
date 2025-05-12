#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# MokuDevice Wrapper 

This module provides a wrapper around the upstream `moku` package's device functionality.
It adds the following features / creature comforts. 

## 1. Environment Variable Integration
The wrapper makes connection parameters configurable through environment variables with sensible defaults:
- `MOKU_FORCE_CONNECT` (default: true)
- `MOKU_IGNORE_BUSY` (default: true)
- `MOKU_PERSIST_STATE` (default: true)
- `MOKU_CONNECT_TIMEOUT` (default: 10)
- `MOKU_READ_TIMEOUT` (default: 10)

This makes the device more flexible for different deployment scenarios.

## 2. Metadata Caching
The wrapper caches device metadata after connection:
- Device name
- Serial number
- Summary information
- Detailed description

## 3. Simplified Interface
The wrapper provides a more consistent and simplified interface for accessing device metadata
through a single `get_metadata()` method, making it easier to work with device information.

## 4. Logging Integration
Integrated Loguru for consistent logging across the application, providing better visibility
into device operations and error conditions.

## 5. Error Handling
Added more robust error handling with proper logging, making it easier to diagnose and
debug issues.

## 6. Connection State Management
Implemented proper connection state management with a dedicated disconnect method that
includes error handling and logging.
"""

import os
from loguru import logger
from moku import Moku

class MokuDevice:
    """A class representing a Moku device connection."""
    
    def __init__(self, ip: str = None):
        """Initialize a new Moku device connection.
        
        Args:
            ip (str, optional): IP address of the Moku device. Defaults to None.
        """
        self.ip = ip
        self.device = None
        self.name = None
        self.serial_number = None
        self.summary = None
        self.describe = None

    def connect(self, force: bool = None) -> bool:
        """Connect to the Moku device.
        
        Args:
            force (bool, optional): Force connection even if device is in use. 
                                  If None, uses MOKU_FORCE_CONNECT env var or defaults to True.
            
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            # Get connection parameters from environment variables with aggressive defaults
            force_connect = force if force is not None else os.getenv('MOKU_FORCE_CONNECT', 'true').lower() == 'true'
            ignore_busy = os.getenv('MOKU_IGNORE_BUSY', 'true').lower() == 'true'
            persist_state = os.getenv('MOKU_PERSIST_STATE', 'true').lower() == 'true'
            connect_timeout = int(os.getenv('MOKU_CONNECT_TIMEOUT', '10'))
            read_timeout = int(os.getenv('MOKU_READ_TIMEOUT', '10'))

            self.device = Moku(
                ip=self.ip,
                force_connect=force_connect,
                ignore_busy=ignore_busy,
                persist_state=persist_state,
                connect_timeout=connect_timeout,
                read_timeout=read_timeout
            )
            logger.info(f"Successfully connected to Moku device at {self.ip}")
            
            # Store additional metadata
            self.name = self.device.name()
            self.serial_number = self.device.serial_number()
            self.summary = self.device.summary()
            self.describe = self.device.describe()
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            return False

    def get_metadata(self):
        """Return stored metadata about the device.
        
        Returns:
            dict: A dictionary containing name, serial_number, summary, and describe.
        """
        return {
            "name": self.name,
            "serial_number": self.serial_number,
            "summary": self.summary,
            "describe": self.describe
        }

    def disconnect(self):
        """Disconnect from the Moku device."""
        if self.device:
            try:
                self.device.relinquish_ownership()
                logger.info("Disconnected from Moku device")
            except Exception as e:
                logger.error(f"Error disconnecting from device: {e}")
