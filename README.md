# Carbon-Intensity-API

A Python library to interface with the Official Carbon Intensity API for Great Britain developed by National Grid ESO. See [carbonintensity.org.uk](https://carbonintensity.org.uk).

## What is this repository for? ##

* A Python interface for the GB Carbon Intensity web API from National Grid ESO.
* Version 0.3
* Developed and tested in Python 3.7, should work with Python 3.6+

## How do I get set up? ##

* Make sure you have Git installed - [Download Git](https://git-scm.com/downloads)
* Run `pip install git+https://github.com/SheffieldSolar/Carbon-Intensity-API`
    - NOTE: You may need to run this command as sudo on Linux machines depending, on your Python installation i.e. `sudo pip install git+https://github.com/SheffieldSolar/Carbon-Intensity-API`

## Getting started ##

See [example.py](https://github.com/SheffieldSolar/Carbon-Intensity-API/blob/master/example.py) for example usage.
```Python
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
```

## Documentation ##

* To do

## How do I upgrade? ##

* Run `pip install --upgrade git+https://github.com/SheffieldSolar/Carbon-Intensity-API`

## Who do I talk to? ##

* Jamie Taylor - [jamie.taylor@sheffield.ac.uk](mailto:jamie.taylor@sheffield.ac.uk "Email Jamie") - [SheffieldSolar](https://github.com/SheffieldSolar)

## Authors ##

* **Jamie Taylor** - *Initial work* - [SheffieldSolar](https://github.com/SheffieldSolar)

## License ##

No license is defined yet - use at your own risk.
