"""
This module is responsible for sending requests to a server.
Keeping the keys and tokens secure is a priority.
Addtionally, it provides a retry strategy for failed requests.

Author: Aaksh Ranjan
Date: 2024-04-12
"""

from constants import OAUTH1_DICT

import copy

from requests import Session
from requests.adapters import HTTPAdapter

from urllib3 import Retry


def get_retry_session(
    retries: int = 3,
    backoff_factor: int = 2,
    status_forcelist: list = [500, 502, 503, 504],
) -> Session:
    """
    Creates a session with a retry strategy.

    Args:
        retries (int): The number of retries to make.
        backoff_factor (int): The backoff factor.
        status_forcelist (list): The status codes to retry on.
    Returns:
        Session: The session with the retry strategy.
    """

    # Create a session.
    session = Session()

    # Define the retry strategy
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)

    # Mount the adapter to the session.
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Return the session.
    return session


class SecureRequester:

    def __init__(
        self,
        client_key: str = None,
        client_secret: str = None,
        resource_owner_key: str = None,
        resource_owner_secret: str = None,
        retries: int = 3,
        backoff_factor: int = 2,
        status_forcelist: list = [500, 502, 503, 504],
    ) -> None:
        """
        Initializes the SecureRequester object.

        Args:
            client_key (str, optional): The client key. Defaults to None.
            client_secret (str, optional): The client secret. Defaults to None.
            resource_owner_key (str, optional): The resource owner key. Defaults to None.
            resource_owner_secret (str, optional): The resource owner secret. Defaults to None.
            retries (int, optional): The number of retries for failed requests. Defaults to 3.
            backoff_factor (int, optional): The backoff factor for retrying requests. Defaults to 2.
            status_forcelist (list, optional): The list of HTTP status codes that should trigger a retry. Defaults to [500, 502, 503, 504].
        """

        # Initialize the authentication dictionary.
        self.__auth = copy.deepcopy(OAUTH1_DICT)
        for key in self.__auth:
            if key in locals():
                self.__auth[key] = locals()[key]
