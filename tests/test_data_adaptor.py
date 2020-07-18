from typing import Generator

import pytest
import requests
from covid19_dashboard.data_adaptor import DEATH_DATA_URL, INFECTIONS_DATA_URL, DataAdaptor


class UnableToConnectToDataSourceError(Exception):
    """raises when the data files are not reachable"""


@pytest.fixture(scope="session")
def data_adaptor() -> Generator[DataAdaptor, None, None]:
    yield DataAdaptor()


def test_data_path_infections():
    response = requests.get(INFECTIONS_DATA_URL)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise UnableToConnectToDataSourceError(f"Unable to access infections data source. Check"
                                               f" your connection and verify that the data are"
                                               f" still available at the source URL: {err}")


def test_data_path_deaths():
    response = requests.get(DEATH_DATA_URL)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise UnableToConnectToDataSourceError(f"Unable to access death data source. Check"
                                               f" your connection and verify that the data are"
                                               f" still available at the source URL: {err}")


def test_data_adaptor__source_data_columns(data_adaptor):
    for value_type, data in data_adaptor.data.items():
        assert all(data.time_series.columns == ['state', 'country', 'date', value_type.value])
        assert all(data.geo_data.columns == ['state', 'country', 'latitude', 'longitude'])

