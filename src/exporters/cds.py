import cdsapi
from pathlib import Path
import certifi
import urllib3
import warnings
from pprint import pprint

from typing import Dict, Optional

from .base import BaseExporter, Region

from pathos.multiprocessing import ProcessingPool as Pool

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()
)


class CDSExporter(BaseExporter):
    """Exports for the Climate Data Store

    cds.climate.copernicus.eu
    """

    def __init__(self, data_folder: Path = Path('data')) -> None:
        super().__init__(data_folder)

        self.client = cdsapi.Client()

    @staticmethod
    def get_era5_times(granularity: str = 'hourly') -> Dict:
        """Returns the era5 selection request arguments
        for the hourly or monthly data

        Parameters
        ----------
        granularity: str, {'monthly', 'hourly'}, default: 'hourly'
            The granularity of data being pulled

        Returns
        ----------
        selection_dict: dict
            A dictionary with all the time-related arguments of the
            selection dict filled out
        """
        years = [str(year) for year in range(1979, 2019 + 1)]
        months = ['{:02d}'.format(month) for month in range(1, 12 + 1)]
        days = ['{:02d}'.format(day) for day in range(1, 31 + 1)]
        times = ['{:02d}:00'.format(hour) for hour in range(24)]

        selection_dict = {
            'year': years,
            'month': months,
            'time': times,
        }
        if granularity == 'hourly':
            selection_dict['day'] = days
        return selection_dict

    @staticmethod
    def create_area(region: Region) -> str:
        """Create an area string for the CDS API from a Region object

        Parameters
        ----------
        region: Region
            A Region to be exported from the CDS warehouse

        Returns
        ----------
        area: str
            A string representing the region which can be passed to the CDS API
        """
        x = [region.latmax, region.lonmin, region.latmin, region.lonmax]

        return "/".join(["{:.3f}".format(x) for x in x])

    @staticmethod
    def make_filename(dataset: str, selection_request: Dict) -> str:
        """Makes the appropriate filename for a CDS export
        """
        date_str = ''
        if 'year' in selection_request:
            years = selection_request['year']
            if len(years) > 1:
                warnings.warn('More than 1 year of data being exported! '
                              'Export times may be significant.')
                years.sort()
                date_str = f'{years[0]}_{years[-1]}'
            else:
                date_str = str(years[0])
        elif 'date' in selection_request:
            date_str = selection_request['date'].replace('/', '_')

        variables = '_'.join(selection_request['variable'])
        output_filename = f'{dataset}_{variables}_{date_str}.nc'
        return output_filename

    def _export(self, dataset: str, selection_request: Dict) -> Path:
        """Export CDS data

        Parameters
        ----------
        dataset: str
            The dataset to be exported
        selection_request: dict
            The selection information to be passed to the CDS API

        Returns
        ----------
        output_file: Path
            The location of the exported data
        """

        output_filename = self.make_filename(dataset, selection_request)
        output_file = self.raw_folder / output_filename

        if not output_file.exists():
            self.client.retrieve(dataset, selection_request, str(output_file))

        return output_file


    @staticmethod
    def _export_monthly_values(year):
        """ export each month separately
        Parameters:
        ----------

        Returns:
        --------

        """
        # create the client for each year responsible for each month
        client = cdsapi.Client()

        months = selection_request['month']

        filepaths = []
        for month in months:
            assert (isinstance(year,str) and isinstance(month,str)), f"For the objects to be JSON serialisable they need to be strings. Currently: year: {type(year)} month: {type(month)}"
            processed_selection_request['month'] = [month]
            processed_selection_request['year'] = [year]


            filepaths.append(self._export(processed_selection_request))

        pass


    def _export_parallel():
        """split the api call into years and run each in parallel

        Functionality:
        -------------
        - Create multiple client instances
            `self.client = cdsapi.Client()`
        - Have each one download a year of data
        """
        years = selection_request['year']

        pool = Pool()
        pool.map(_export_monthly_values, years)
        for year in years:
            # export_annual_values()
            # _export_monthly_values()
            pass
        pass


class ERA5Exporter(CDSExporter):
    """Exports ERA5 data from the Climate Data Store

    cds.climate.copernicus.eu
    """
    @staticmethod
    def get_era5_times(granularity: str = 'hourly') -> Dict:
        """Returns the era5 selection request arguments
        for the hourly or monthly data

        Parameters
        ----------
        granularity: str, {'monthly', 'hourly'}, default: 'hourly'
            The granularity of data being pulled

        Returns
        ----------
        selection_dict: dict
            A dictionary with all the time-related arguments of the
            selection dict filled out
        """
        years = [str(year) for year in range(1979, 2019 + 1)]
        months = ['{:02d}'.format(month) for month in range(1, 12 + 1)]
        days = ['{:02d}'.format(day) for day in range(1, 31 + 1)]
        times = ['{:02d}:00'.format(hour) for hour in range(24)]

        selection_dict = {
            'year': years,
            'month': months,
            'time': times,
        }
        if granularity == 'hourly':
            selection_dict['day'] = days
        return selection_dict

    @staticmethod
    def get_datastore(variable: str) -> str:
        pressure_level_variables = {
            'divergence', 'fraction_of_cloud_cover', 'geopotential',
            'ozone_mass_mixing_ratio', 'potential_vorticity', 'relative_humidity',
            'specific_cloud_ice_water_content', 'specific_cloud_liquid_water_content',
            'specific_humidity', 'specific_rain_water_content', 'specific_snow_water_content',
            'temperature', 'u_component_of_wind', 'v_component_of_wind', 'vertical_velocity',
            'vorticity'
        }

        if variable in pressure_level_variables:
            return 'pressure-levels'
        else:
            return 'single-levels'

    @staticmethod
    def print_api_request(selection_request: Dict,
                          dataset: str,) -> None:
        """TODO: should this be implemented as a nice `__repr__` method?"""
        print("------------------------")
        print("Dataset:")
        print(f"'{dataset}'")
        print("------------------------")
        print("Selection Request:")
        pprint(selection_request)
        print("------------------------")

        return

    def create_selection():
        pass


    def export(self,
               variable: str,
               dataset: Optional[str] = None,
               granularity: str = 'hourly',
               show_api_request: bool = False,
               selection_request: Optional[Dict] = None,
               dummy_run=False) -> Path:

        # setup the default selection request
        processed_selection_request = {
            'product_type': 'reanalysis',
            'format': 'netcdf',
            'variable': [variable]
        }
        for key, val in self.get_era5_times(granularity).items():
            processed_selection_request[key] = val

        # by default, we investigate Kenya
        kenya_region = self.get_kenya()
        processed_selection_request['area'] = self.create_area(kenya_region)

        if dataset is None:
            dataset = f'reanalysis-era5-{self.get_datastore(variable)}'
            if granularity == 'monthly':
                dataset = f'{dataset}-monthly-means'

        # override with arguments passed by the user
        if selection_request is not None:
            for key, val in selection_request.items():
                # TODO: we should catch and deal with these errors
                assert all([isinstance(val,str) for val in val]), f"For the dictionary to be JSON serialisable the values must be strings. First value of your list of '{key}': {type(val[0])}\n'{key}': {val}"
                processed_selection_request[key] = val

        if show_api_request:
            self.print_api_request(processed_selection_request, dataset)

        if dummy_run:
            # only printing the api request
            return
        else:
            return self._export(dataset, processed_selection_request)
