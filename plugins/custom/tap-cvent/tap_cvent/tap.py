"""cvent tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_cvent import streams


class Tapcvent(Tap):
    """cvent tap class."""

    name = "tap-cvent"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "Cvent_OAuth_key",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The key to authenticate against the API service"
        ),
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            secret=False,  # Flag config as protected.
            description="API client ID"
        ),
        th.Property(
            "scope",
            th.StringType,
            required=True,
            secret=False,  # Flag config as protected.
            description="scope for request fo OAuth token"
        )
    ).to_dict()
    #     th.Property(
    #         "project_ids",
    #         th.ArrayType(th.StringType),
    #         required=True,
    #         description="Project IDs to replicate",
    #     ),
    #     th.Property(
    #         "start_date",
    #         th.DateTimeType,
    #         description="The earliest record date to sync",
    #     ),
    #     th.Property(
    #         "api_url",
    #         th.StringType,
    #         default="https://api.mysample.com",
    #         description="The url for the API service",
    #     ),
    # ).to_dict()

    def discover_streams(self) -> list[streams.cventStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.EventsStream(self),
        ]


if __name__ == "__main__":
    Tapcvent.cli()
