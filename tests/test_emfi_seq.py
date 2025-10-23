#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for EMFI-Seq module.

This script tests the EMFI-Seq module by importing it and verifying
that the class and methods are available.

Usage:
    python -m tests.test_emfi_seq
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import the moku_go package
sys.path.insert(0, str(Path(__file__).parent.parent))

from moku_go import MokuEMFISeq


class TestEMFISeq(unittest.TestCase):
    """Test case for EMFI-Seq module."""

    def test_import(self):
        """Test that the EMFI-Seq module can be imported."""
        self.assertIsNotNone(MokuEMFISeq)
        
    def test_methods(self):
        """Test that the EMFI-Seq class has the expected methods."""
        # Create an instance
        emfi = MokuEMFISeq(ip="127.0.0.1")  # Dummy IP for testing
        
        # Check that the methods exist
        self.assertTrue(hasattr(emfi, "connect"))
        self.assertTrue(hasattr(emfi, "set_stair_levels"))
        self.assertTrue(hasattr(emfi, "set_delays"))
        self.assertTrue(hasattr(emfi, "enable_sequencer"))
        self.assertTrue(hasattr(emfi, "disable_sequencer"))
        self.assertTrue(hasattr(emfi, "get_status"))
        self.assertTrue(hasattr(emfi, "disconnect"))


if __name__ == "__main__":
    unittest.main()