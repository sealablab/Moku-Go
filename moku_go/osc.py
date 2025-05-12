#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from loguru import logger
from moku.instruments import Oscilloscope
from typing import Optional, Dict, Any

class MokuOscilloscope:
    """A class representing a Moku oscilloscope instrument."""
    
    def __init__(self, ip: str, force_connect: bool = None):
        """Initialize a new Moku oscilloscope connection.
        
        Args:
            ip (str): IP address of the Moku device
            force_connect (bool, optional): Force connection even if device is in use.
                                          If None, uses MOKU_FORCE_CONNECT env var or defaults to True.
        """
        self.ip = ip
        self.force_connect = force_connect
        self.scope = None

    def connect(self) -> bool:
        """Connect to the oscilloscope instrument.
        
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            # Get connection parameters from environment variables with aggressive defaults
            force_connect = self.force_connect if self.force_connect is not None else os.getenv('MOKU_FORCE_CONNECT', 'true').lower() == 'true'
            ignore_busy = os.getenv('MOKU_IGNORE_BUSY', 'true').lower() == 'true'
            persist_state = os.getenv('MOKU_PERSIST_STATE', 'true').lower() == 'true'
            connect_timeout = int(os.getenv('MOKU_CONNECT_TIMEOUT', '10'))
            read_timeout = int(os.getenv('MOKU_READ_TIMEOUT', '10'))

            self.scope = Oscilloscope(
                ip=self.ip,
                force_connect=force_connect,
                ignore_busy=ignore_busy,
                persist_state=persist_state,
                connect_timeout=connect_timeout,
                read_timeout=read_timeout
            )
            logger.info(f"Successfully connected to oscilloscope at {self.ip}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to oscilloscope: {e}")
            return False

    def configure(self, config: Dict[str, Any]) -> bool:
        """Configure the oscilloscope with the given settings.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary containing scope settings
            
        Returns:
            bool: True if configuration successful, False otherwise.
        """
        if not self.scope:
            logger.error("Oscilloscope not connected")
            return False
            
        try:
            # Configure input sources if specified
            if 'sources' in config:
                for channel, source in config['sources'].items():
                    self.scope.set_source(int(channel), source)
            
            # Configure trigger if specified
            if 'trigger' in config:
                trigger = config['trigger']
                self.scope.set_trigger(
                    type=trigger.get('type', 'Edge'),
                    source=trigger.get('source', 'Input1'),
                    level=trigger.get('level', 0.01)
                )
            
            # Configure timebase if specified
            if 'timebase' in config:
                timebase = config['timebase']
                self.scope.set_timebase(
                    timebase.get('start', -5e-6),
                    timebase.get('end', 5e-6)
                )
            
            return True
        except Exception as e:
            logger.error(f"Failed to configure oscilloscope: {e}")
            return False

    def get_data(self) -> Optional[Dict[str, Any]]:
        """Get data from the oscilloscope.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing captured data, or None if failed
        """
        if not self.scope:
            logger.error("Oscilloscope not connected")
            return None
            
        try:
            data = self.scope.get_data()
            return data
        except Exception as e:
            logger.error(f"Failed to get data from oscilloscope: {e}")
            return None

    def disconnect(self):
        """Disconnect from the oscilloscope."""
        if self.scope:
            try:
                self.scope.relinquish_ownership()
                logger.info("Disconnected from oscilloscope")
            except Exception as e:
                logger.error(f"Error disconnecting from oscilloscope: {e}") 