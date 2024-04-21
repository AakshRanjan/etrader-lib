"""
This module is responsible for sending requests to a server.
Keeping the keys and tokens secure is a priority.
Addtionally, it provides a retry strategy for failed requests.

Author: Aaksh Ranjan
Date: 2024-04-12
"""

import logging

from requests import Session
from requests.models import Response
from requests.adapters import HTTPAdapter

from requests_oauthlib import OAuth1Session
from urllib3 import Retry


logger = logging.getLogger(__name__)


class SecureRequester:
    """
    A class to send secure requests to a server. It provides a retry strategy for failed requests.
    This class is designed to be multi-thread safe.
    """

    def __init__(
        self,
        client_key: str = None,
        client_secret: str = None,
        resource_owner_key: str = None,
        resource_owner_secret: str = None,
        callback_uri: str = None,
        retries: int = 3,
        backoff_factor: int = 2,
        status_forcelist: list = None,
        debug: bool = False,
    ) -> None:
        """
        Initializes the SecureRequester object.

        Args:
            client_key (str): The client key for the OAuth1 session.
            client_secret (str): The client secret for the OAuth1 session.
            resource_owner_key (str): The resource owner key for the OAuth1 session.
            resource_owner_secret (str): The resource owner secret for the OAuth1 session.
            callback_uri (str): The callback URI for the OAuth1 session.

            retries (int, optional): The number of retries for the request.
                Defaults to 3.
            backoff_factor (int, optional): The backoff factor for the request.
                Defaults to 2.
            status_forcelist (list, optional): The status codes to retry on.
                Defaults to [500, 502, 503, 504].
            debug (bool, optional): The debug flag.
                Defaults to False.
        Returns:
            None
        """

        # Initialize the public attributes.
        self.retries = retries
        self.backoff_factor = backoff_factor
        if status_forcelist is None:
            self.status_forcelist = [500, 502, 503, 504]
        else:
            self.status_forcelist = status_forcelist
        self.debug = debug

        # Initialize the Private attributes.
        self.__client_key = client_key
        self.__client_secret = client_secret
        self.__resource_owner_key = resource_owner_key
        self.__resource_owner_secret = resource_owner_secret
        self.__callback_uri = callback_uri

        # Set the logger level.
        if self.debug:
            logger.setLevel(logging.DEBUG)

        # Check if the client key and client secret are provided.
        if self.__client_key is None or self.__client_secret is None:
            logger.debug(
                "Client Key is %s and Client Secret is %s",
                client_key,
                client_secret,
            )
            raise ValueError("Client key and client secret are required.")

    def get_retry_session(self) -> Session:
        """
        Creates a session with a retry strategy.

        Args:
            None
        Returns:
            Session: The session with the retry strategy.
        """

        # Create a Oauth1 session.
        session = OAuth1Session(
            client_key=self.__client_key,
            client_secret=self.__client_secret,
            resource_owner_key=self.__resource_owner_key,
            resource_owner_secret=self.__resource_owner_secret,
            callback_uri=self.__callback_uri,
        )

        # Define the retry strategy
        retry = Retry(
            total=self.retries,
            read=self.retries,
            connect=self.retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)

        # Mount the adapter to the session.
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Return the session.
        return session

    def get(
        self, url: str, params: dict = None, timeout: int = 10
    ) -> Response:
        """
        Sends a GET request to the server.

        Args:
            url (str): The URL to send the request to.
            params (dict, optional): The parameters for the request. Defaults to None.

        Returns:
            dict: The response from the server.
        """

        # Create a session with a retry strategy.
        session = self.get_retry_session()

        # Send the GET request.
        response = session.get(url, params=params, timeout=timeout)

        # Close the session.
        session.close()

        # Return the response.
        return response

    def post(self, url: str, data: dict = None, timeout: int = 10) -> Response:
        """
        Sends a POST request to the server.

        Args:
            url (str): The URL to send the request to.
            data (dict, optional): The data for the request. Defaults to None.

        Returns:
            dict: The response from the server.
        """

        # Create a session with a retry strategy.
        session = self.get_retry_session()

        # Send the POST request.
        response = session.post(url, data=data, timeout=timeout)

        # Close the session.
        session.close()

        # Return the response.
        return response

    def put(self, url: str, data: dict = None, timeout: int = 10) -> Response:
        """
        Sends a PUT request to the server.

        Args:
            url (str): The URL to send the request to.
            data (dict, optional): The data for the request. Defaults to None.

        Returns:
            dict: The response from the server.
        """

        # Create a session with a retry strategy.
        session = self.get_retry_session()

        # Send the PUT request.
        response = session.put(url, data=data, timeout=timeout)

        # Close the session.
        session.close()

        # Return the response.
        return response

    def delete(
        self, url: str, data: dict = None, timeout: int = 10
    ) -> Response:
        """
        Sends a DELETE request to the server.

        Args:
            url (str): The URL to send the request to.

        Returns:
            dict: The response from the server.
        """

        # Create a session with a retry strategy.
        session = self.get_retry_session()

        # Send the DELETE request.
        response = session.delete(url, data=data, timeout=timeout)

        # Close the session.
        session.close()

        # Return the response.
        return response
