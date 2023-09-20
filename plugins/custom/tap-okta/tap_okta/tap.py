"""okta tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_okta import streams


class TapOkta(Tap):
    """okta tap class."""

    name = "tap-okta"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "api_url",
            th.StringType,
            required=True,
            description="The url for the API service",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.oktaStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.UsersStream(self),
        ]


if __name__ == "__main__":
    TapOkta.cli()
