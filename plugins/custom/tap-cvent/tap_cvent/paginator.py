from singer_sdk.pagination import BaseHATEOASPaginator

class CventPaginator(BaseHATEOASPaginator):
    def get_next_url(self, response):
        data = response.json()
        if data["paging"]["_links"].get("next"):
            return data["paging"]["_links"]["next"]["href"]
        else:
            return None