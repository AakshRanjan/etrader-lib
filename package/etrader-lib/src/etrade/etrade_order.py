"""
This module contains the Etrade class which is used to interact with the Etrade API.
It provides methods to place orders, and more.

Author: Aaksh Ranjan
Date: 2024-04-12
"""

from . import SecureRequester


class ETradeOrder:
    """
    A class to interact with the Etrade API.
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
    ) -> None:
        """
        Initializes the Etrade Order object.
        """
        if not secure_requester or not client_key and not client_secret and not resource_owner_key and not resource_owner_secret:
            raise ValueError("You must provide either a SecureRequester object or the required keys and secrets.")
        
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
            self.base_url = "https://apisb.etrade.com"
        else:
            self.base_url = "https://api.etrade.com"
        
    def create_preview_order(self, *args, **kwargs) -> dict:
        """
        Checks if the order parameters are valid.
        """
        pass
        