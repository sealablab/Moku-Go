#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

    def connect(self, force: bool = False) -> bool:
        """Connect to the Moku device.
        
        Args:
            force (bool, optional): Force connection even if device is in use. Defaults to False.
            
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            self.device = Moku(ip=self.ip, force_connect=force)
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
