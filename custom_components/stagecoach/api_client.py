import aiohttp, uuid, time, pytz
from datetime import datetime, timezone

class StagecoachApiClient:

  def __init__(self):
    self._base_url = 'https://android.stagecoachbus.com'
    self._fingerprint = str(uuid.uuid4())
    self._secret = 'nvwPVASmd25Rd6HVg54' # Hardcoded into the app

  async def async_get_anonymous_token(self):
    """Get an anonymous token"""
    async with aiohttp.ClientSession() as client:
      url = f'{self._base_url}/authentication/clientCredentialsGrant'
      async with client.post(url, headers={
        'X-SC-AppVersion': '1.1',
        'X-SC-Fingerprint': self._fingerprint,
        'X-SC-DeviceInfo': 'Android13',
        'Content-Type': 'application/x-www-form-urlencoded'
      }, data=f'grant_type=client_credentials&client_id=stagecoachmobile&client_secret={self._secret}') as response:
        data = await response.json()
        return data['access_token']

  async def async_get_stop_data(self, stop):
    """Get the stop data for a given stop"""
    
    # Get the time in ms
    curTime = time.time()
    timeMs = round(curTime * 1000)

    access_token = await self.async_get_anonymous_token()

    async with aiohttp.ClientSession() as client:
      url = f'{self._base_url}/adc/stop-monitor'
      async with client.post(url, headers={
        'X-SC-Timestamp': str(timeMs),
        'X-SC-Nonce': str(uuid.uuid4()).upper(),
        'X-SC-Fingerprint': self._fingerprint,
        'X-SC-AppVersion': '1.1',
        'Authorization': 'Bearer ' + access_token,
        'X-SC-securityMethod': 'API',
        'X-SC-apiKey': self._secret,
        'Content-Type': 'application/x-www-form-urlencoded', # This looks wrong but it's what the app sends
      }, data="{\"stopMonitorRequest\":{\"lookAheadMinutes\":60,\"stopMonitorQueries\":{\"stopMonitorQuery\":[{\"stopPointLabel\":\"" + stop + "\",\"servicesFilters\":{\"servicesFilter\":[]}}]},\"header\":{\"channel\":\"mobile\",\"ipAddress\":\"\",\"retailOperation\":\"ukbus\"}}}") as response:
        data = await response.json()
        if (len(data['stopMonitors']) == 0):
          return []
        return data['stopMonitors']['stopMonitor'][0]['monitoredCalls']['monitoredCall']

  def _reformat_time(self, time_input):
    return datetime.strptime(time_input, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC).astimezone(datetime.now().astimezone().tzinfo).strftime("%H:%M")

  async def async_get_bus_times(self, stop):
    """Get the bus times for a given stop"""
    data = await self.async_get_stop_data(stop)
    return list(map(lambda departure: {
      "due": self._reformat_time(departure["expectedArrivalTime"]) if 'expectedArrivalTime' in departure else self._reformat_time(departure["aimedArrivalTime"]),
      "service_ref": departure["lineRef"],
      "service_number": departure["lineRef"],
      "destination": departure["destinationDisplay"],
      "is_live": True if 'expectedArrivalTime' in departure else False
    }, data))