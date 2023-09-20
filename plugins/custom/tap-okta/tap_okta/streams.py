"""Stream type classes for tap-okta."""

from __future__ import annotations

from pathlib import Path
from singer_sdk import typing as th  # JSON Schema typing helpers
from tap_okta.client import oktaStream
import requests
from typing import Any, Dict, Optional, Iterable
from urllib.parse import urlparse, parse_qs
from urllib import parse

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class UsersStream(oktaStream):
    """Define custom stream."""

    replication_method = "INCREMENTAL"
    replication_key = "lastUpdated"
    
    records_jsonpath = "$[*]"
    name = "users"
    path = "/api/v1/users"
    primary_keys = ["id"]
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("status", th.StringType),
        th.Property("created", th.StringType),
        th.Property("activated", th.StringType),
        th.Property("statusChanged", th.StringType),
        th.Property("lastLogin", th.StringType),
        th.Property("lastUpdated", th.DateTimeType),
        th.Property("passwordChanged", th.DateTimeType),
        th.Property("lastUpdated", th.DateTimeType),
        th.Property(
            "type", th.ObjectType(
                th.Property("id", th.StringType),
            )
        ),
        th.Property("profile", th.ObjectType(
            th.Property("country", th.StringType),
            th.Property("email", th.StringType),
            th.Property("firstName", th.StringType),
            th.Property("hylandSfdcId", th.StringType),
            th.Property("isExistingCustomer", th.StringType),
            th.Property("lastName", th.StringType),
            th.Property("login", th.StringType),
            th.Property("mobilePhone", th.StringType),
            th.Property("organization", th.StringType),
            th.Property("secondEmail", th.StringType),
            th.Property("statusExceptionReason", th.StringType),
        )),
        th.Property("credentials", th.ObjectType(
            th.Property("emails", th.ArrayType(
                th.ObjectType(
                    th.Property("status", th.StringType),
                    th.Property("type", th.StringType),
                    th.Property("value", th.StringType),
                )
            )),
            th.Property("provider", th.ObjectType(
                th.Property("name", th.StringType),
                th.Property("type", th.StringType),
            )),
        ),
        )
    ).to_dict()

    def get_url_params(self, context, next_page_token):
        params = {}

        if next_page_token:
            params["after"] = next_page_token
        
        starting_date = self.get_starting_timestamp(context)
        if starting_date:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

            # Convert Meltano datetime format to API datetime format
            starting_date = starting_date.format("YYYY-MM-DDTHH:mm:ss.SSS") + 'Z'
            filter_string = f'{self.replication_key}+gt+"{starting_date}"'

            params["filter"] = filter_string
            params = parse.urlencode(params, safe=":+")

        return params

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Any:
        """Return token identifying next page or None if all records have been read.

        Args:
            response: A raw `requests.Response`_ object.
            previous_token: Previous pagination reference.

        Returns
            Reference value to retrieve next page.

        .. _requests.Response:
            https://docs.python-requests.org/en/latest/api/#requests.Response
        """
        """Return a token for identifying next page or None if no more pages."""

        resp_header = response.headers["Link"]
        response_links = requests.utils.parse_header_links(resp_header)

        for link in response_links:
            if link["rel"] == "next":
                next_page_url = link["url"]
                next_page_token = self.parse_next_page_token(next_page_url)
            else:
                next_page_token = None
        return next_page_token
    
    def parse_next_page_token(self, next_page_url):
        """Parse next page token from next_page_url and return code."""

        parsed_url = urlparse(next_page_url)
        query = parse_qs(parsed_url.query)
        after_param = query["after"].pop()

        return after_param
    