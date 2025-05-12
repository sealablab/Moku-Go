#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
            return True
        except Exception as e:
            logger.error(f"Failed to connect to device: {e}")
            return False

    def disconnect(self):
        """Disconnect from the Moku device."""
        if self.device:
            try:
                self.device.relinquish_ownership()
                logger.info("Disconnected from Moku device")
            except Exception as e:
                logger.error(f"Error disconnecting from device: {e}")
