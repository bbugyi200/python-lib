"""Overly general Python library used when no other library is a good fit."""

import logging as _logging


__author__ = "Bryan M Bugyi"
__email__ = "bryanbugyi34@gmail.com"
__version__ = "0.11.0"

_logging.getLogger(__name__).addHandler(_logging.NullHandler())
