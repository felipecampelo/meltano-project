"""REST client handling, including cventStream base class."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Iterable
from datetime import datetime, timedelta

import requests
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator  # noqa: TCH002
from singer_sdk.streams import RESTStream
from urllib.parse import parse_qsl
import os

from tap_cvent.auth import cventAuthenticator
from tap_cvent.paginator import CventPaginator

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from cached_property import cached_property

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class cventStream(RESTStream):
    """cvent stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        # TODO: hardcode a value here, or retrieve it from self.config
        return "https://api-platform.cvent.com/ea"

    records_jsonpath = "$.data[*]"  # Or override `parse_response`.

    # Set this value or override `get_new_paginator`.
    # next_page_token_jsonpath = "$.next_page"  # noqa: S105

    @cached_property
    def authenticator(self) -> _Auth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        
        return cventAuthenticator.create_for_stream(self)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    # def get_new_paginator(self) -> BaseAPIPaginator:
    def get_new_paginator(self) -> CventPaginator:
        """Create a new pagination helper instance.

        If the source API can make use of the `next_page_token_jsonpath`
        attribute, or it contains a `X-Next-Page` header in the response
        then you can remove this method.

        If you need custom pagination that uses page numbers, "next" links, or
        other approaches, please read the guide: https://sdk.meltano.com/en/v0.25.0/guides/pagination-classes.html.

        Returns:
            A pagination helper instance.
        """
        return CventPaginator()
        # return super().get_new_paginator()

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params.update(parse_qsl(next_page_token.query))
        if self.replication_key:
            params["sort"] = "start:ASC"
            # params["order_by"] = self.replication_key

        if os.environ.get('MELTANO_ENVIRONMENT') == "dev":
            current_date = datetime.now()
            yesterday = current_date - timedelta(days=1)
            starting_date = yesterday.strftime("%Y-%m-%dT%H:%M:%S.%f") + 'Z'
        else:
            starting_date = self.get_starting_replication_key_value(context)
            
        if starting_date:
            # params["after"] = starting_date.isoformat()
            params["after"] = starting_date

        return params

    def prepare_request_payload(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: Any | None,  # noqa: ARG002
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
        return None

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        # TODO: Parse response body and return a set of records.
        # yield response.json()["paging"]
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

    # def post_process(
    #     self,
    #     row: dict,
    #     context: dict | None = None,  # noqa: ARG002
    # ) -> dict | None:
    #     """As needed, append or transform raw data to match expected structure.

    #     Args:
    #         row: An individual record from the stream.
    #         context: The stream context.

    #     Returns:
    #         The updated record dictionary, or ``None`` to skip the record.
    #     """
    #     # TODO: Delete this method if not needed.
    #     return row
