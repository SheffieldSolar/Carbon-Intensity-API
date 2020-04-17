#!/usr/bin/env python3

"""
A Python library for interfacing with the National Grid Carbon Intensity API.

- Jamie Taylor <jamie.taylor@sheffield.ac.uk>
- First Authored: 2020-04-17
"""

import json
from datetime import datetime, timedelta, date
from time import sleep
import requests
import pandas as pd
from numpy import nan

class CarbonIntensityAPI:
    """
    Interface with the NG ESO Carbon Intensity web API.
    
    Parameters
    ----------
    `retries` : int
        Optionally specify the number of retries to use should the API respond with anything
        other than status code 200. Exponential back-off applies inbetween retries.
    """
    def __init__(self, retries=3):
        self.base_url = "https://api.carbonintensity.org.uk"
        self.max_range = {"national": timedelta(days=14), "regional": timedelta(days=14)}
        self.retries = retries
        self.headers = {"Accept": "application/json"}

    def between(self, start, end, type="national"):
        """
        Get the Carbon Intensity forecast and actual results for a given time interval from the API.

        Parameters
        ----------
        `start` : datetime
            A timezone-aware datetime object. Will be corrected to the END of the half hour in which
            *start* falls, since ESO use end of interval as convention.
        `end` : datetime
            A timezone-aware datetime object. Will be corrected to the END of the half hour in which
            *end* falls, since ESO use end of interval as convention.
        `type` : str
            Either "national" or "regional".
        Returns
        -------
        Pandas DataFrame
            Carbon intensity data for the requested period.
        Notes
        -----
        For list of optional *extra_fields*, see `PV_Live API Docs
        <https://www.solar.sheffield.ac.uk/pvlive/api/>`_.
        """
        type_check = not (isinstance(start, datetime) and isinstance(end, datetime))
        tz_check = start.tzinfo is None or end.tzinfo is None
        if type_check or tz_check:
            raise Exception("Start and end must be timezone-aware Python datetime objects.")
        start = self._nearest_hh(start)
        end = self._nearest_hh(end)
        type = type.lower()
        if type not in ("national", "regional"):
            raise Exception("Type must be either 'national' or 'regional'.")
        endpoint = "/regional/intensity/{}/{}" if type == "regional" else "/intensity/{}/{}"
        carbon = None
        gen_mix = None
        request_start = start
        max_range = self.max_range[type]
        while request_start < end:
            request_end = min(end, request_start + self.max_range[type] - timedelta(minutes=30))
            request_endpoint = endpoint.format(request_start.isoformat(), request_end.isoformat())
            url = f"{self.base_url}{request_endpoint}"
            response = self.query_api(url)
            data = self._parse_fromto_json(response, type)
            carbon_ = data if type == "national" else data[0]
            gen_mix_ = None if type == "national" else data[1]
            if carbon is None:
                carbon = carbon_
            else:
                carbon = pd.concat((carbon, carbon_), ignore_index=True)
            if gen_mix is None:
                gen_mix = gen_mix_
            else:
                gen_mix = pd.concat((gen_mix, gen_mix_), ignore_index=True)
            request_start += self.max_range[type]
        return carbon, gen_mix

    def _parse_fromto_json(self, response, type):
        """Parse the response from the /{from}/{to} endpoints into Pandas DataFrame."""
        if type == "national":
            data_list = [
                [d["to"], d["intensity"].get("forecast", nan), d["intensity"].get("actual", nan),
                d["intensity"]["index"]] for d in response["data"]
            ]
            data = pd.DataFrame(data_list, columns=["timestamp", "forecast", "actual", "index"])
            data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True, infer_datetime_format=True)
            return data
        else:
            carbon_list = []
            fuel_mix_labels = ["biomass", "coal", "imports", "gas", "nuclear", "other", "hydro",
                               "solar", "wind"]
            fuel_mix_list = []
            for datum in response["data"]:
                for region in datum["regions"]:
                    carbon_list.append([datum["to"], region["regionid"],
                                        region["intensity"].get("forecast", nan),
                                        region["intensity"].get("actual", nan),
                                        region["intensity"]["index"]])
                    fuel_mix = {f["fuel"]: f["perc"] for f in region["generationmix"]}
                    fuel_mix_list.append([datum["to"], region["regionid"]] +
                                         [fuel_mix[l] for l in fuel_mix_labels])
            carbon_data = pd.DataFrame(carbon_list, columns=["timestamp", "regionid", "forecast",
                                                             "actual", "index"])
            carbon_data["timestamp"] = pd.to_datetime(carbon_data["timestamp"], utc=True,
                                                      infer_datetime_format=True)
            fuel_mix_data = pd.DataFrame(fuel_mix_list,
                                         columns=["timestamp", "regionid"] + fuel_mix_labels)
            fuel_mix_data["timestamp"] = pd.to_datetime(fuel_mix_data["timestamp"], utc=True,
                                                      infer_datetime_format=True)
            return carbon_data, fuel_mix_data

    def query_api(self, url):
        """Query the API."""
        return self._fetch_url(url)

    def _fetch_url(self, url):
        """Fetch the URL with GET request."""
        success = False
        try_counter = 0
        delay = 1
        while not success and try_counter < self.retries + 1:
            try_counter += 1
            try:
                page = requests.get(url, params={}, headers=self.headers)
                page.raise_for_status()
                success = True
            except requests.exceptions.HTTPError:
                sleep(delay)
                delay *= 2
                continue
            except:
                raise
        if not success:
            raise Exception("Error communicating with the Carbon Intensity API.")
        try:
            return page.json()
        except:
            raise Exception("Error communicating with the Carbon Intensity API.")

    def _nearest_hh(self, dt):
        """Round a given datetime object up to the nearest hafl hour."""
        if not(dt.minute % 30 == 0 and dt.second == 0 and dt.microsecond == 0):
            dt = dt - timedelta(minutes=dt.minute%30, seconds=dt.second) + timedelta(minutes=30)
        return dt

def main():
    """Demo the module's capabilities."""
    import pytz
    api = CarbonIntensityAPI()
    print("National between 2020-04-01 00:00 and 2020-04-17 14:00: ")
    carbon_data = api.between(datetime(2020, 4, 1, 0, 30, tzinfo=pytz.utc),
                              datetime(2020, 4, 17, 14, 00, tzinfo=pytz.utc))
    print(carbon_data)
    print("Regional between 2020-04-01 00:00 and 2020-04-17 14:00: ")
    carbon_data, gen_mix_data = api.between(datetime(2020, 4, 1, 0, 30, tzinfo=pytz.utc),
                                            datetime(2020, 4, 17, 14, 00, tzinfo=pytz.utc),
                                            type="regional")
    print(carbon_data)
    print(gen_mix_data)

if __name__ == "__main__":
    main()
