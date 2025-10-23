#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
# EMFI-Seq Module for Moku-Go

This module provides functionality for deploying and controlling the EMFI-Seq
bitstream on Moku:Go devices.

## Control Register Map (matches modules/EMFI-Seq/top/Top.vhd):
    Control0[31]:    Enable (inverted: 1=disabled, 0=enabled)
    Control0[30]:    Clock enable (inverted: 1=frozen, 0=running)
    Control0[7:0]:   Clock divider select (0=÷1, 1=÷2, ..., 255=÷256)
    Control1[6:0]:   State 1 delay (7-bit)
    Control2[6:0]:   State 2 delay (7-bit)
    Control3[6:0]:   State 3 delay (7-bit)
    Control4[6:0]:   State 4 delay (7-bit)
    Control5[15:0]:  State 1 DAC level (signed 16-bit, -5V to +5V)
    Control6[15:0]:  State 2 DAC level (signed 16-bit, -5V to +5V)
    Control7[15:0]:  State 3 DAC level (signed 16-bit, -5V to +5V)
    Control8[15:0]:  State 4 DAC level (signed 16-bit, -5V to +5V)

## Output Map:
    OutputA[15:0]:   DAC stair-step output (signed 16-bit)
    OutputB[6:0]:    FSM sticky status (bits 0-3: S1-S4 entry markers)
    OutputC[3:0]:    Current state (one-hot)
    OutputC[15:4]:   Monitor value MSBs
    OutputD[7:0]:    Clock divider counter status
"""

import os
from loguru import logger
from moku.instruments import MultiInstrument, CloudCompile, Oscilloscope
from typing import Optional, Dict, Any, Tuple


class MokuEMFISeq:
    """A class representing a Moku EMFI-Seq instrument."""
    
    def __init__(self, ip: str = None):
        """Initialize a new Moku EMFI-Seq connection.
        
        Args:
            ip (str, optional): IP address of the Moku device. Defaults to None.
        """
        self.ip = ip
        self.multi_instrument = None
        self.emfi_seq = None
        self.oscilloscope = None
        
    def connect(self, bitstream_path: str, force: bool = None) -> bool:
        """Connect to the Moku device and deploy EMFI-Seq bitstream.
        
        Args:
            bitstream_path (str): Path to .bit bitstream file
            force (bool, optional): Force connection even if device is in use. 
                                  If None, uses MOKU_FORCE_CONNECT env var or defaults to True.
            
        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            # Get connection parameters from environment variables with aggressive defaults
            force_connect = force if force is not None else os.getenv('MOKU_FORCE_CONNECT', 'true').lower() == 'true'
            
            logger.info(f"Connecting to Moku at {self.ip}...")
            self.multi_instrument = MultiInstrument(
                self.ip, 
                platform_id=2, 
                force_connect=force_connect
            )
            
            # Deploy EMFI-Seq bitstream to Slot 1
            logger.info(f"Deploying bitstream: {bitstream_path}")
            try:
                # Try with explicit file path
                import os
                abs_path = os.path.abspath(bitstream_path)
                logger.info(f"Using absolute path: {abs_path}")
                self.emfi_seq = self.multi_instrument.set_instrument(1, CloudCompile, bitstream=abs_path)
            except Exception as e:
                logger.error(f"Failed to deploy with absolute path: {e}")
                raise
            
            # Set up Oscilloscope in Slot 2 for monitoring
            logger.info("Setting up Oscilloscope in Slot 2...")
            self.oscilloscope = self.multi_instrument.set_instrument(2, Oscilloscope)
            
            # Route EMFI-Seq DAC output to oscilloscope and front panel
            logger.info("Routing signals...")
            connections = [
                dict(source="Slot1OutA", destination="Slot2InA"),  # DAC stair-step to scope
                dict(source="Slot1OutA", destination="Output1"),   # DAC to front panel
                dict(source="Slot1OutB", destination="Slot2InB"),  # Status to scope
            ]
            self.multi_instrument.set_connections(connections=connections)
            
            # Configure EMFI-Seq with default parameters
            logger.info("Configuring EMFI-Seq Control registers...")
            
            # Control0: Enable=0 (disabled), ClkEn=0 (running), DivSel=0 (÷1)
            # Bit layout: [31]=1 (disabled), [30]=0 (running), [7:0]=0 (÷1)
            self.emfi_seq.set_control(0, 0x80000000)
            
            # State delays (7-bit values, 0-127 cycles)
            self.emfi_seq.set_control(1, 10)  # S1 delay: 10 cycles
            self.emfi_seq.set_control(2, 20)  # S2 delay: 20 cycles
            self.emfi_seq.set_control(3, 30)  # S3 delay: 30 cycles
            self.emfi_seq.set_control(4, 40)  # S4 delay: 40 cycles
            
            # Stair-step DAC levels (16-bit signed, Moku voltage mapping)
            # -5V = 0x8000, 0V = 0x0000, +5V = 0x7FFF
            # Default: 1.1V, 1.2V, 1.3V, 1.4V (ascending staircase)
            self.emfi_seq.set_control(5, 0x199A)  # S1: 1.1V = 6554
            self.emfi_seq.set_control(6, 0x1EB8)  # S2: 1.2V = 7864
            self.emfi_seq.set_control(7, 0x23D7)  # S3: 1.3V = 9175
            self.emfi_seq.set_control(8, 0x28F5)  # S4: 1.4V = 10485
            
            # Configure oscilloscope for stair-step monitoring
            logger.info("Configuring Oscilloscope...")
            self.oscilloscope.set_timebase(-1e-3, 1e-3)  # ±1ms window
            # Use the correct source names for the oscilloscope
            self.oscilloscope.set_source(1, "In1")       # Channel 1: DAC stair-step
            self.oscilloscope.set_source(2, "In2")       # Channel 2: Status
            
            logger.info("EMFI-Seq deployment complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy EMFI-Seq: {e}")
            if self.multi_instrument:
                self.multi_instrument.relinquish_ownership()
                self.multi_instrument = None
                self.emfi_seq = None
                self.oscilloscope = None
            return False
    
    def set_stair_levels(self, s1_v: float, s2_v: float, s3_v: float, s4_v: float) -> bool:
        """Configure stair-step voltage levels.
        
        Args:
            s1_v, s2_v, s3_v, s4_v: Voltages in range [-5.0, +5.0] V
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.emfi_seq:
            logger.error("EMFI-Seq not connected")
            return False
            
        try:
            logger.info(f"Setting stair levels: {s1_v}V, {s2_v}V, {s3_v}V, {s4_v}V")
            
            for i, voltage in enumerate([s1_v, s2_v, s3_v, s4_v], start=5):
                if voltage < -5.0 or voltage > 5.0:
                    raise ValueError(f"Voltage {voltage}V out of range [-5.0, +5.0]")
                # Moku mapping: -5V=0x8000 (-32768), +5V=0x7FFF (+32767)
                code = int((voltage / 5.0) * 32767)
                self.emfi_seq.set_control(i, code & 0xFFFF)  # Ensure 16-bit unsigned for register write
                
            return True
        except Exception as e:
            logger.error(f"Failed to set stair levels: {e}")
            return False
    
    def set_delays(self, s1_delay: int, s2_delay: int, s3_delay: int, s4_delay: int) -> bool:
        """Configure state delays.
        
        Args:
            s1_delay, s2_delay, s3_delay, s4_delay: Delays in cycles (0-127)
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.emfi_seq:
            logger.error("EMFI-Seq not connected")
            return False
            
        try:
            for i, delay in enumerate([s1_delay, s2_delay, s3_delay, s4_delay], start=1):
                if delay < 0 or delay > 127:
                    raise ValueError(f"Delay {delay} out of range [0, 127]")
                self.emfi_seq.set_control(i, delay)
                
            logger.info(f"Delays set: S1={s1_delay}, S2={s2_delay}, S3={s3_delay}, S4={s4_delay} cycles")
            return True
        except Exception as e:
            logger.error(f"Failed to set delays: {e}")
            return False
    
    def enable_sequencer(self) -> bool:
        """Enable EMFI-Seq sequencer (clear Control0[31]).
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.emfi_seq:
            logger.error("EMFI-Seq not connected")
            return False
            
        try:
            logger.info("Enabling sequencer...")
            self.emfi_seq.set_control(0, 0x00000000)  # Enable=0, ClkEn=0, DivSel=0
            return True
        except Exception as e:
            logger.error(f"Failed to enable sequencer: {e}")
            return False
    
    def disable_sequencer(self) -> bool:
        """Disable EMFI-Seq sequencer (set Control0[31]).
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.emfi_seq:
            logger.error("EMFI-Seq not connected")
            return False
            
        try:
            logger.info("Disabling sequencer...")
            self.emfi_seq.set_control(0, 0x80000000)  # Enable=1 (inverted), ClkEn=0, DivSel=0
            return True
        except Exception as e:
            logger.error(f"Failed to disable sequencer: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the EMFI-Seq.
        
        Returns:
            Dict[str, Any]: Dictionary containing status information.
        """
        if not self.emfi_seq or not self.oscilloscope:
            logger.error("EMFI-Seq not connected")
            return {"connected": False}
            
        try:
            # Read output registers to get status
            output_a = self.emfi_seq.get_monitor(0)  # DAC stair-step output
            output_b = self.emfi_seq.get_monitor(1)  # FSM sticky status
            output_c = self.emfi_seq.get_monitor(2)  # Current state (one-hot)
            output_d = self.emfi_seq.get_monitor(3)  # Clock divider counter status
            
            # Extract current state from one-hot encoding
            current_state = 0
            if output_c & 0x01:
                current_state = 1
            elif output_c & 0x02:
                current_state = 2
            elif output_c & 0x04:
                current_state = 3
            elif output_c & 0x08:
                current_state = 4
                
            # Convert DAC output to voltage
            dac_voltage = (output_a / 32767.0) * 5.0 if output_a < 32768 else ((output_a - 65536) / 32768.0) * 5.0
            
            return {
                "connected": True,
                "dac_output": dac_voltage,
                "current_state": current_state,
                "fsm_status": output_b & 0x0F,  # Lower 4 bits are state entry markers
                "clock_counter": output_d & 0xFF,
                "raw": {
                    "output_a": output_a,
                    "output_b": output_b,
                    "output_c": output_c,
                    "output_d": output_d
                }
            }
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"connected": False, "error": str(e)}
    
    def disconnect(self):
        """Disconnect from the Moku device."""
        if self.multi_instrument:
            try:
                self.multi_instrument.relinquish_ownership()
                logger.info("Disconnected from Moku device")
            except Exception as e:
                logger.error(f"Error disconnecting from device: {e}")
            finally:
                self.multi_instrument = None
                self.emfi_seq = None
                self.oscilloscope = None