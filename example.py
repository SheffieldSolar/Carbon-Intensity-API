#!/usr/bin/env python3

"""
Minimal example usage for the Carbon-Intensity-API library.

- Jamie Taylor <jamie.taylor@sheffield.ac.uk>
- First Authored: 2020-04-17
"""

from datetime import datetime
import pytz

from carbon_intensity_api import CarbonIntensityAPI

def main():
    api = CarbonIntensityAPI()
    print("National between 2020-04-01 00:00 and 2020-04-17 14:00: ")
    carbon_data, _ = api.between(datetime(2020, 4, 1, 0, 30, tzinfo=pytz.utc),
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
