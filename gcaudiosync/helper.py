"""This file contains some helper functions for the gcaudiosync package."""

import sys


def debugger_is_active() -> bool:
    """Return if the debugger is currently active"""
    return hasattr(sys, "gettrace") and sys.gettrace() is not None
