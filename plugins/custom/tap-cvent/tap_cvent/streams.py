"""Stream type classes for tap-cvent."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_cvent.client import cventStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.

class EventsStream(cventStream):
    """Define custom stream."""

    name = "cvent__events"
    path = "/events"
    schema_filepath = SCHEMAS_DIR / "data.json"  # noqa: ERA001

    # records_jsonpath = "$.response.data[*]"  # Or override `parse_response`.
    primary_keys = ["id"]
    replication_key = "lastModified"