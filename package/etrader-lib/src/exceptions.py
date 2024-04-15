"""
This module contains the custom exceptions that are raised by the etrader-lib package.

Author: Aaksh Ranjan
Date: 2024-04-14
"""


class EtradeException(Exception):
    """Base exception class for the Etrade package."""

    def __init__(self, message="An error occurred."):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"


class InvalidTradeException(EtradeException):
    """Exception raised for invalid trade requests."""

    def __init__(self, message="Invalid trade request."):
        super().__init__(message)
