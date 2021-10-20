import logging
import re
import aiohttp
from .const import (
  REGEX_TIME,
  REGEX_TIME_MINS,
)

from datetime import (timedelta)
from homeassistant.util.dt import (now, as_local, parse_datetime)

_LOGGER = logging.getLogger(__name__)

class FirstBusApiClient:

  def __init__(self):
    self._base_url = 'https://www.firstbus.co.uk'

  async def async_get_next_bus(self, stop, buses):
    """Get the user's account"""
    async with aiohttp.ClientSession() as client:
      auth = aiohttp.BasicAuth(self._api_key, '')
      url = f'{self._base_url}/getNextBus?stop={stop}'
      async with client.get(url, auth=auth) as response:
        # Disable content type check as sometimes it can report text/html
        data = await response.json(content_type=None)

        if ("times" in data):
          for time in data["times"]:
            if (time["serviceNumber"] in buses):
              matches = re.search(REGEX_TIME, time["Due"])
              if (matches != None):
                local_now = now()
                time["Due"] = as_local(parse_datetime(local_now.strftime(f"%Y-%m-%dT{time['Due']}{local_now.strftime('%z')}")))
              else:
                matches = re.search(REGEX_TIME_MINS, time["Due"])
                if (matches == None):
                  raise Exception(f'Unable to extract due time: {time["Due"]}')
                
                local_now = now()
                time["Due"] = as_local(parse_datetime(local_now.strftime(f"%Y-%m-%dT%H:{matches[1]}{local_now.strftime('%z')}")))

              if (time["Due"] < now()):
                time["Due"] = time["Due"] + timedelta(days=1)

              return time
        
        return None