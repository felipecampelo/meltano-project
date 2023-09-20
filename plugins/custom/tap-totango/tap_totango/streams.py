"""Stream type classes for tap-totango."""

from __future__ import annotations

from pathlib import Path
import typing as t

import json
from singer_sdk import typing as th
from singer_sdk._singerlib import Schema
from singer_sdk.tap_base import Tap  # JSON Schema typing helpers
from tap_totango.paginator import TotangoAccountsPaginator, TotangoUsersPaginator, TotangoEventsPaginator, TotangoTouchpointsPaginator
import os

from tap_totango.client import totangoStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class AccountsStream(totangoStream):
    """Define custom stream."""

    name = "accounts"
    rest_method = "POST"
    path = "/api/v1/search/accounts"
    records_jsonpath = "$.response.accounts.hits[*]"
    primary_keys = ["name"]
    schema_filepath = SCHEMAS_DIR / "accounts.json"  # noqa: ERA001

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        params = self.config

        if next_page_token:
            offset = next_page_token
        else:
            offset = params["accounts_offset"]
        query = {
            "terms": params["accounts_terms"],
            "fields": params["accounts_fields"],
            "offset": offset,
            "count": params["accounts_count"],
            "sort_by": params["accounts_sort_by"],
            "sort_order": params["accounts_sort_order"],
        }
        data = {"query": json.dumps(query)}
        return data

    def get_child_context(self, record: dict, context: t.Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "account_id": record["name"],
        }

    def get_new_paginator(self) -> TotangoAccountsPaginator:
        start_value = self.config['accounts_offset']
        page_size = self.config['accounts_count']
        return TotangoAccountsPaginator(start_value, page_size)


class UsersStream(totangoStream):
    """Define custom stream."""

    replication_method = "INCREMENTAL"
    replication_key = "last_activity_time"
    name = "users"
    rest_method = "POST"
    path = "/api/v1/search/users"
    records_jsonpath = "$.response.users.hits[*]"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "users.json"  # noqa: ERA001

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        params = self.config

        if os.environ.get('MELTANO_ENVIRONMENT') == "dev":
            dev_dict = {"type": "date", "term": "last_activity_time", "joker": "yesterday"}
            params["users_terms"].insert(0, dev_dict)
        else:
            incremental_value = self.get_starting_replication_key_value(context)
            if incremental_value is not None:
                incremental_dict = {'type': 'date', 'term': 'last_activity_time', 'gt': incremental_value}
                params["users_terms"].insert(0, incremental_dict)

        if next_page_token:
            offset = next_page_token
        else:
            offset = params["users_offset"]
        query = {
            "terms": params["users_terms"],
            "fields": params["users_fields"],
            "offset": offset,
            "count": params["users_count"],
            # "sort_by": params["users_sort_by"],
            # "sort_order": params["users_sort_order"],
        }
        data = {"query": json.dumps(query)}
        return data

    def get_new_paginator(self) -> TotangoUsersPaginator:
        start_value = self.config['users_offset']
        page_size = self.config['users_count']
        return TotangoUsersPaginator(start_value, page_size)


class EventsStream(totangoStream):
    """Define custom stream."""

    replication_method = "INCREMENTAL"
    replication_key = "timestamp"
    name = "events"
    rest_method = "POST"
    path = "/api/v2/events/search"
    records_jsonpath = "$.response.events.hits[*]"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "events.json"  # noqa: ERA001

    def get_new_paginator(self) -> TotangoEventsPaginator:
        start_value = self.config['events_offset']
        page_size = self.config['events_count']
        return TotangoEventsPaginator(start_value, page_size)
    
    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        params = self.config
        
        if os.environ.get('MELTANO_ENVIRONMENT') == "dev":
            dev_dict = {"type": "date", "term": "date", "joker": "yesterday"}
            params["events_terms"].insert(0, dev_dict)
        else:
            incremental_value = self.get_starting_replication_key_value(context)
            if incremental_value is not None:
                incremental_dict = {'type': 'date', 'term': 'date', 'gt': incremental_value}
                params["events_terms"].insert(0, incremental_dict)
        # else:
            # First load to prod
        # incremental_dict = {'type': 'date', 'term': 'date', 'lte': 1688567961000}
        # params["events_terms"].insert(0, incremental_dict)

        if next_page_token:
            offset = next_page_token
        else:
            offset = params["events_offset"]
        query = {
            "terms": params["events_terms"],
            "fields": [],
            "offset": offset,
            "count": params["events_count"],
        }
        data = {"query": json.dumps(query)}
        # if context.get("account_id"):
        #     data["account_id"] = context.get('account_id')
        if params.get("account_id"):
            data["account_id"] = params["account_id"]
        return data

class Touchpoints(totangoStream):
    """Define custom stream."""

    name = "touchpoints"
    rest_method = "POST"
    path = "/api/v1/search/accounts/collections"
    records_jsonpath = "$.response.collections.hits[*]"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "touchpoints.json" 

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        params = self.config

        if next_page_token:
            offset = next_page_token
        else:
            offset = params["touchpoints_offset"]
        query = {
            "terms": params["touchpoints_terms"],
            "fields": params["touchpoints_fields"],
            "offset": offset,
            "count": params["touchpoints_count"],
            "parent_account_fields": params["touchpoints_parent_account_fields"],
        }
        data = {"query": json.dumps(query)}
        return data

    def get_new_paginator(self) -> TotangoTouchpointsPaginator:
        start_value = self.config['touchpoints_offset']
        page_size = self.config['touchpoints_count']
        return TotangoTouchpointsPaginator(start_value, page_size)

    def post_process(
        self,
        row: dict,
        context: dict | None = None,  # noqa: ARG002
    ) -> dict | None:
        """As needed, append or transform raw data to match expected structure.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        if isinstance(row['selected_fields'][4], type(None)):
            row['selected_fields'][4] = []

        row["account_service_id"] = str(row["account"]["service_id"])
        row["account_name"] = str(row["account"]["name"])
        row["touchpoint_subject"] = str(row["selected_fields"][0])
        row["touchpoint_type"] = str(row["selected_fields"][1])
        row["success_flow"] = str(row["selected_fields"][2])
        row["created"] = str(row["selected_fields"][3])
        row["contacts"] = row["selected_fields"][4]
        row["internal_users"] = str(row["selected_fields"][5])
        row["reasons"] = str(row["selected_fields"][6])
        row["participant_roles"] = str(row["selected_fields"][7])
        row["creator"] = str(row["selected_fields"][8])
        row["last_updated"] = str(row["selected_fields"][9])

        row.pop("account")
        row.pop("selected_fields")

        return row

class TouchpointTypes(totangoStream):
    """Stream to get touchpoint types"""

    records_jsonpath = "$[*]"
    name = "touchpoint_types"
    path = "/api/v3/touchpoint-types"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "touchpoint_types.json"

    def prepare_request_payload(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict | None:
        return None

class TouchpointTags(totangoStream):
    """Stream to get touchpoint tags"""

    records_jsonpath = "$[*]"
    name = "touchpoint_tags"
    path = "/api/v3/touchpoint-tags"
    primary_keys = ["id"]
    schema_filepath = SCHEMAS_DIR / "touchpoint_tags.json"

    def prepare_request_payload(
        self,
        context: dict | None,  
        next_page_token: Any | None,  
    ) -> dict | None:
        return None
    