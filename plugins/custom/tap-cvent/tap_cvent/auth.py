"""cvent Authentication."""

from __future__ import annotations
import base64
import requests
from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta
from singer_sdk.helpers._util import utc_now


# The SingletonMeta metaclass makes your streams reuse the same authenticator instance.
# If this behavior interferes with your use-case, you can remove the metaclass.
class cventAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """Authenticator class for cvent."""


        # Authentication and refresh
    def update_access_token(self) -> None:
        """Update `access_token` along with: `last_refreshed` and `expires_in`.

        Raises:
            RuntimeError: When OAuth login fails.
        """
        request_time = utc_now()

        sample_string = self.config.get("Cvent_OAuth_key", "")
        sample_string_bytes = sample_string.encode("ascii")

        base64_bytes = base64.b64encode(sample_string_bytes)
        base64_string = base64_bytes.decode("ascii")

        headers = {
            'Authorization':'Basic '+base64_string,
            'Content-Type':'application/x-www-form-urlencoded'
            }

        auth_request_payload = self.oauth_request_payload
        token_response = requests.post(
            self.auth_endpoint,
            data=auth_request_payload,
            headers=headers,
            timeout=60,
        )
        try:
            token_response.raise_for_status()
        except requests.HTTPError as ex:
            msg = f"Failed OAuth login, response was '{token_response.json()}'. {ex}"
            raise RuntimeError(msg) from ex

        self.logger.info("OAuth authorization attempt was successful.")

        token_json = token_response.json()
        self.access_token = token_json["access_token"]
        self.expires_in = token_json.get("expires_in", self._default_expiration)
        if self.expires_in is None:
            self.logger.debug(
                "No expires_in receied in OAuth response and no "
                "default_expiration set. Token will be treated as if it never "
                "expires.",
            )
        self.last_refreshed = request_time

    @property
    def auth_headers(self) -> dict:
        """Return a dictionary of auth headers to be applied.

        These will be merged with any `http_headers` specified in the stream.

        Returns:
            HTTP headers for authentication.
        """
        if not self.is_token_valid():
            self.update_access_token()
        result = super().auth_headers
        result["Authorization"] = f"Bearer {self.access_token}"
        result["Accept"] = "application/json"
        return result

    @property
    def oauth_request_body(self) -> dict:
        """Define the OAuth request body for the AutomaticTestTap API.

        Returns:
            A dict with the request body
        """
        # TODO: Define the request body needed for the API.
        return {
            'grant_type':'client_credentials',
            'client_id':self.config.get('client_id'),
            'scope':self.config.get('scope'),
            }


        # return {
        #     "resource": "https://analysis.windows.net/powerbi/api",
        #     "scope": self.oauth_scopes,
        #     "client_id": self.config["client_id"],
        #     "username": self.config["username"],
        #     "password": self.config["password"],
        #     "grant_type": "password",
        # }

    @classmethod
    def create_for_stream(cls, stream) -> cventAuthenticator:  # noqa: ANN001
        """Instantiate an authenticator for a specific Singer stream.

        Args:
            stream: The Singer stream instance.

        Returns:
            A new authenticator.
        """
        return cls(
            stream=stream,
            auth_endpoint="https://api-platform.cvent.com/ea/oauth2/token",
            oauth_scopes="event/events:read",
        )
