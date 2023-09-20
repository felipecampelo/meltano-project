from singer_sdk.pagination import BaseOffsetPaginator
from abc import ABCMeta, abstractmethod
from requests import Response
import typing as t


class TotangoAccountsPaginator(BaseOffsetPaginator):
      
    def has_more(self, response: Response) -> bool:
        data = response.json()
        total_hits = data.get('response').get('accounts').get('total_hits')
        if self._value + self._page_size >= total_hits:
            return False
        else:
            return True

class TotangoUsersPaginator(BaseOffsetPaginator):
      
    def has_more(self, response: Response) -> bool:
        data = response.json()
        total_hits = data.get('response').get('users').get('total_hits')
        if self._value + self._page_size >= total_hits:
            return False
        else:
            return True

class TotangoEventsPaginator(BaseOffsetPaginator):
      
    def has_more(self, response: Response) -> bool:
        data = response.json()
        total_hits = data.get('response').get('events').get('total_hits')
        if self._value + self._page_size >= total_hits:
            return False
        else:
            return True
        
class TotangoTouchpointsPaginator(BaseOffsetPaginator):
      
    def has_more(self, response: Response) -> bool:
        data = response.json()
        total_hits = data.get('response').get('collections').get('total_hits')
        if self._value + self._page_size >= total_hits:
            return False
        else:
            return True