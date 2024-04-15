"""
This module contains the ETradeMarket class which is used to interact with the ETrade Market API.
It provides methods to fetch market data, search for securities, and more.

Author: Aaksh Ranjan
Date: 2024-04-14
"""

import threading
import uuid

from . import SecureRequester


class ETradeMarket:
    """
    A class to interact with the ETrade Market API.
    """

    def __init__(
        self,
        secure_requester: SecureRequester = None,
        sandbox: bool = False,
        client_key: str = None,
        client_secret: str = None,
        resource_owner_key: str = None,
        resource_owner_secret: str = None,
        retries: int = 3,
        backoff_factor: int = 2,
        status_forcelist: list = [500, 502, 503, 504],
    ):
        """
        Initializes the Etrade Order object.

        Args:
            secure_requester (SecureRequester, optional): The SecureRequester object. Defaults to None.
            sandbox (bool, optional): Whether to use the sandbox environment. Defaults to False.
            client_key (str, optional): The client key. Defaults to None.
            client_secret (str, optional): The client secret. Defaults to None.
            resource_owner_key (str, optional): The resource owner key. Defaults to None.
            resource_owner_secret (str, optional): The resource owner secret. Defaults to None.
            retries (int, optional): The number of retries for failed requests. Defaults to 3.
            backoff_factor (int, optional): The backoff factor for retrying requests. Defaults to 2.
            status_forcelist (list, optional): The list of HTTP status codes that should trigger a retry. Defaults to [500, 502, 503, 504].
        Returns:
            None
        """
        if (
            not secure_requester
            or not client_key
            and not client_secret
            and not resource_owner_key
            and not resource_owner_secret
        ):
            raise ValueError(
                "You must provide either a SecureRequester object or the required keys and secrets."
            )

        if not secure_requester:
            self.__secure_requester = SecureRequester(
                client_key=client_key,
                client_secret=client_secret,
                resource_owner_key=resource_owner_key,
                resource_owner_secret=resource_owner_secret,
                retries=retries,
                backoff_factor=backoff_factor,
                status_forcelist=status_forcelist,
            )
        else:
            self.__secure_requester = secure_requester

        if sandbox:
            self.base_url = "https://apisb.etrade.com/v1/market/"
        else:
            self.base_url = "https://api.etrade.com/v1/market/"

        # Initialize the symbols_data attribute.
        # This attribute will store the symbols that are being tracked.
        # Example: {"AAPL": {"symbol": "AAPL", "price": 150.0}, ...}
        self.symbols_data = {}

        # Initialize the symbols_tracker attribute.
        # This attribute will store the thread that is updating the price and
        # the corresponding list symbols that are being tracked by the thread.
        # Example: {<Thread(Thread-1, started 1234)>: ["AAPL", "GOOGL"], ...}
        self.symbols_tracker = {}

    def add_symbols(self, symbols: list) -> None:
        """
        Creates a tracker for the given symbols.

        Args:
            symbol (list): A list of symbols to track.
        Returns:
            None
        """

        # Check if the symbols list is empty.
        if len(symbols) == 0:
            raise ValueError("You must provide at least one symbol to track.")

        for symbol in symbols:
            # Check if the symbol is already being tracked.
            if symbol in self.symbols_data:
                raise ValueError(
                    f"The symbol {symbol} is already being tracked."
                )

            # Check if there is a thread available to track the symbol.
            if len(self.symbols_tracker) > 0:
                # Find a thread that is not full.
                for thread, symbols in self.symbols_tracker.items():
                    if not thread.is_tracker_full():
                        thread.add_symbol(symbol)
                        break
                    else:
                        continue
            else:
                # Create a new thread to track the symbol.
                thread = SymbolTracker(
                    base_url=self.base_url,
                    symbols_data=self.symbols_data,
                    symbol=symbol,
                    secure_requester=self.__secure_requester,
                )
                thread.start()
                self.symbols_tracker[thread] = [symbol,]

            # Add the symbol to the symbols_data attribute.
            self.symbols_data[symbol] = {"symbol": symbol, "price": None}

    def remove_symbols(self, symbols: list) -> None:
        """
        Removes the given symbols from the tracker.

        Args:
            symbol (list): A list of symbols to remove.
        Returns:
            None
        """

        # Check if the symbols list is empty.
        if len(symbols) == 0:
            raise ValueError("You must provide at least one symbol to remove.")

        for symbol in symbols:
            # Check if the symbol is being tracked.
            if symbol not in self.symbols_data:
                raise ValueError(
                    f"The symbol {symbol} is not being tracked."
                )

            # Remove the symbol from the symbols_data attribute.
            del self.symbols_data[symbol]

            # Find the thread that is tracking the symbol.
            for thread, symbols in self.symbols_tracker.items():
                if symbol in symbols:
                    thread.remove_symbol(symbol)
                    if len(thread.symbols) == 0:
                        thread.join()
                        del self.symbols_tracker[thread]
                    break

class SymbolTracker(threading.Thread):
    """
    A class to track the price of a symbol.
    """

    def __init__(
        self,
        base_url: str,
        symbols_data: dict,
        symbol: str,
        secure_requester: SecureRequester,
    ):
        """
        Initializes the SymbolTracker object.

        Args:
            symbol (str): The symbol to track (e.g., "AAPL").
            base_url (str): The base URL for the API.
            secure_requester (SecureRequester): The SecureRequester object.
        Returns:
            None
        """

        super(SymbolTracker, self).__init__()

        self.symbols = [
            symbol,
        ]
        self.symbols_data = symbols_data
        self.base_url = base_url
        self.secure_requester = secure_requester

    def is_tracker_full(self):
        """
        Checks if the tracker is full.

        Returns:
            bool: True if the tracker is full, False otherwise.
        """

        return len(self.symbols) >= 25

    def add_symbol(self, symbol):
        """
        Adds a symbol to the tracker.

        Args:
            symbol (str): The symbol to add.
        Returns:
            None
        """

        if self.is_tracker_full():
            raise ValueError("The tracker is full.")

        self.symbols.append(symbol)

        return self.symbols

    def remove_symbol(self, symbol):
        """
        Removes a symbol from the tracker.

        Args:
            symbol (str): The symbol to remove.
        Returns:
            None
        """

        if symbol not in self.symbols:
            raise ValueError(
                "The symbol is not being tracked by this tracker."
            )

        self.symbols.remove(symbol)

        return self.symbols
    
    def get_prices(self):
        """
        Gets the latest prices for the symbols being tracked.

        Returns:
            dict: A dictionary of symbols and their prices.
        """

        # Create the URL for the API request.
        url = f"{self.base_url}/quote/{','.join(self.symbols)}.json"

        # Send the GET request to the API.
        response = self.secure_requester.get(url).json()


        # Parse the response and extract the prices.
        prices = {}
        for quote in response["QuoteResponse"]["QuoteData"]:
            symbol = quote["symbol"]
            price = quote["All"]["lastTrade"]
            prices[symbol] = price

        return prices

    def run(self):
        """
        Runs the tracker.

        Returns:
            None
        """

        while len(self.symbols) > 0:
            # Get the latest prices for the symbols.
            prices = self.get_prices()

            # Update the symbols_data attribute with the latest prices.
            for symbol, price in prices.items():
                self.symbols_data[symbol] = {"symbol": symbol, "price": price}