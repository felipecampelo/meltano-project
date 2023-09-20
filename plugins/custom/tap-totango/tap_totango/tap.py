"""totango tap class."""

from __future__ import annotations

from typing import List

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_totango import streams

true = True  # to facilitate examples, doc purposes


class Taptotango(Tap):
    """totango tap class."""

    name = "tap-totango"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_url",
            th.StringType,
            default="https://api.totango.com",
            required=True,
            allowed_values=["https://api.totango.com", "https://api-eu1.totango.com "],
            description="The url for the API services. https://api.totango.com is for US services, whereas https://api-eu1.totango.com is for EU services.",
        ),
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "events_terms",
            th.ArrayType(
                th.ObjectType(
                    th.Property("type", th.StringType, required=True),
                    additional_properties=True,
                )
            ),
            required=True,
            default=[],
            description="An array containing filter conditions to use for the events stream search.",
            examples=[
                [{"type": "event_property", "name": "event_type", "eq": "note"}],
                [
                    {
                        "type": "or",
                        "or": [
                            {
                                "type": "event_property",
                                "name": "event_type",
                                "eq": "note",
                            },
                            {
                                "type": "event_property",
                                "name": "event_type",
                                "eq": "campaign_touch",
                            },
                        ],
                    }
                ],
                [
                    {"type": "date", "term": "date", "joker": "yesterday"},
                    {
                        "type": "or",
                        "or": [
                            {
                                "type": "event_property",
                                "name": "event_type",
                                "eq": "note",
                            },
                            {
                                "type": "event_property",
                                "name": "event_type",
                                "eq": "campaign_touch",
                            },
                        ],
                    },
                ],
                [
                    {"type": "date", "term": "date", "gte": 1587859200000},
                    {"type": "event_property", "name": "event_type", "eq": "note"},
                ],
            ],
        ),
        th.Property(
            "events_count",
            th.IntegerType,
            required=True,
            default=997,
            description="The maximum number of accounts to return in the events result set. The max. value for count is 1000.",
        ),
        th.Property(
            "events_offset",
            th.IntegerType,
            required=True,
            default=0,
            description="Page number (0 is the 1st-page).",
        ),
        th.Property(
            "account_id",
            th.StringType,
            description="Filter the events stream results for a specific account.",
        ),
        th.Property(
            "accounts_terms",
            th.ArrayType(
                th.ObjectType(
                    th.Property("type", th.StringType, required=True),
                    additional_properties=True,
                )
            ),
            required=True,
            default=[],
            description="An array containing filter conditions to use for the accounts stream search.",
            examples=[
                [{"type": "string", "term": "status_group", "in_list": ["paying"]}]
            ],
        ),
        th.Property(
            "accounts_fields",
            th.ArrayType(
                th.ObjectType(
                    th.Property("type", th.StringType, required=True),
                    additional_properties=True,
                )
            ),
            required=True,
            default=[],
            description="List of fields to return as results. Note that the account name and account-id are always returned as well.",
            examples=[
                [
                    {
                        "type": "string",
                        "term": "health",
                        "field_display_name": "Health rank ",
                    },
                    {
                        "type": "health_trend",
                        "field_display_name": "Health last change ",
                    },
                    {
                        "type": "string_attribute",
                        "attribute": "Success Manager",
                        "field_display_name": "Success Manager",
                    },
                ]
            ],
        ),
        th.Property(
            "accounts_count",
            th.IntegerType,
            default=997,
            description="The maximum number of accounts to return in the accounts result set. The max. value for count is 1000.",
        ),
        th.Property(
            "accounts_offset",
            th.IntegerType,
            default=0,
            description='Record number (0 states "start at record 0"). The record size can be defined using the count parameter (and limited to 1000). Tip: To page through results, ask for 1000 records (count: 1000). If you receive 1000 records, assume there’s more, in which case you want to pull the next 1000 records (offset: 1000…then 2000…etc.). Repeat paging until the number of records returned is less than 1000.',
        ),
        th.Property(
            "accounts_sort_by",
            th.StringType,
            default="display_name",
            description="Field name to sort the accounts stream results set by.",
        ),
        th.Property(
            "accounts_sort_order",
            th.StringType(allowed_values=["ASC", "DESC"]),
            default="ASC",
            description="Order to sort the accounts stream results set by.",
        ),
        th.Property(
            "users_terms",
            th.ArrayType(
                th.ObjectType(
                    th.Property("type", th.StringType, required=True),
                    additional_properties=True,
                )
            ),
            required=True,
            default=[],
            description="An array containing filter conditions to use for the users stream search.",
            examples=[
                [
                    {
                        "type": "parent_account",
                        "terms": [
                            {
                                "type": "string",
                                "term": "status_group",
                                "in_list": ["paying"],
                            }
                        ],
                    }
                ]
            ],
        ),
        th.Property(
            "users_fields",
            th.ArrayType(
                th.ObjectType(
                    th.Property("type", th.StringType, required=True),
                    additional_properties=True,
                )
            ),
            required=True,
            default=[],
            description="List of fields to return as results. Note that the user name and id along with account name and account-id are always returned as well.",
            examples=[
                [
                    {
                        "type": "date",
                        "term": "last_activity_time",
                        "field_display_name": "Last activity",
                        "desc": true,
                    },
                    {
                        "type": "named_aggregation",
                        "aggregation": "total_activities",
                        "duration": 14,
                        "field_display_name": "Activities (14d)",
                    },
                ]
            ],
        ),
        th.Property(
            "users_count",
            th.IntegerType,
            default=997,
            description="The maximum number of users to return in the users result set. The max. value for count is 1000.",
        ),
        th.Property(
            "users_offset",
            th.IntegerType,
            default=0,
            description='Record number (0 states "start at record 0"). The record size can be defined using the count parameter (and limited to 1000). Tip: To page through results, ask for 1000 records (count: 1000). If you receive 1000 records, assume there’s more, in which case you want to pull the next 1000 records (offset: 1000…then 2000…etc.). Repeat paging until the number of records returned is less than 1000.',
        ),
        th.Property(
            "users_sort_by",
            th.StringType,
            default="display_name",
            description="Field name to sort the users stream results set by.",
        ),
        th.Property(
            "users_sort_order",
            th.StringType(allowed_values=["ASC", "DESC"]),
            default="ASC",
            description="Order to sort the users stream results set by.",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.totangoStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.EventsStream(self),
            streams.AccountsStream(self),
            streams.UsersStream(self),
            streams.TouchpointTags(self),
            streams.TouchpointTypes(self),
            streams.Touchpoints(self),
        ]


if __name__ == "__main__":
    Taptotango.cli()
