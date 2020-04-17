try:
    #py2
    from carbon_intensity_api import CarbonIntensityAPI
except:
    #py3+
    from carbon_intensity_api.carbon_intensity_api import CarbonIntensityAPI

__all__ = ["CarbonIntensityAPI"]
