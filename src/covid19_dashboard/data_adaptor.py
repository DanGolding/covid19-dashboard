from enum import Enum
from typing import Optional, List, Union, Iterable, Tuple, NamedTuple

import pandas as pd

INFECTIONS_DATA_URL = (r"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
                       r"csse_covid_19_data/csse_covid_19_time_series/"
                       r"time_series_covid19_confirmed_global.csv")
DEATH_DATA_URL = (r"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
                  r"csse_covid_19_data/csse_covid_19_time_series/"
                  r"time_series_covid19_deaths_global.csv")

STATE = "state"
COUNTRY = "country"
LATITUDE = "latitude"
LONGITUDE = "longitude"
DATE = "date"


class ValueType(Enum):
    INFECTIONS = "infections"
    DEATHS = "deaths"


class DataSets(NamedTuple):
    time_series: pd.DataFrame
    geo_data: pd.DataFrame


class DataAdaptor:

    def __init__(self,
                 infection_data_path: Optional[str] = None,
                 death_data_path: Optional[str] = None):

        self.infection_data_path = infection_data_path or INFECTIONS_DATA_URL
        self.death_data_path = death_data_path or DEATH_DATA_URL
        self.data = {
            ValueType.INFECTIONS: DataSets(*self._get_data(ValueType.INFECTIONS)),
            ValueType.DEATHS: DataSets(*self._get_data(ValueType.DEATHS)),
        }

    @property
    def countries(self) -> List[str]:
        return self.data[ValueType.INFECTIONS].time_series["country"].unique().tolist()

    def _get_data(self, type_: ValueType) -> Tuple[pd.DataFrame, pd.DataFrame]:

        if type_ == ValueType.INFECTIONS:
            data_path = self.infection_data_path
        elif type_ == ValueType.DEATHS:
            data_path = self.death_data_path
        else:
            raise ValueError("Unsupported value type {type_}")

        data_raw = pd.read_csv(data_path)
        column_names_old = data_raw.columns[:4].values
        column_names_new = [STATE, COUNTRY, LATITUDE, LONGITUDE]
        data_raw = data_raw.rename(
            columns={old: new for old, new in zip(column_names_old,column_names_new)})
        data_no_geo_coords = data_raw.drop(columns=[LATITUDE,
                                                    LONGITUDE])

        time_series_data = data_no_geo_coords.melt(value_vars=data_no_geo_coords.columns[2:],
                                                   id_vars=data_no_geo_coords.columns[:2],
                                                   var_name=DATE,
                                                   value_name=type_.value)
        time_series_data[DATE] = pd.to_datetime(
            time_series_data[DATE])
        geo_data = data_raw.iloc[:, :4].drop_duplicates()

        return time_series_data, geo_data

    def get_time_series_for_country(self,
                                    type_: ValueType,
                                    countries: Union[str, Iterable[str]],
                                    index_since_: Optional[int] = 0) -> pd.DataFrame:
        if isinstance(countries, str):
            countries = [countries]
        # TODO - make it case insensitive
        # countries = [country.title() for country in countries]

        if index_since_:
            return self._get_time_series_for_country_days(type_, countries, index_since_)
        else:
            return self._get_time_series_for_country_by_date(type_, countries)

    def _get_time_series_for_country_by_date(
            self, type_: ValueType, countries: List[str]) -> pd.DataFrame:
        """Return a time series of total infections for specific countries

        :param countries: A list of country names
        :return:
        """
        time_series_data = self.data[type_].time_series
        filtered_data = time_series_data[
            time_series_data[COUNTRY].isin(countries)]
        filtered_data = (filtered_data[[COUNTRY,
                                        DATE,
                                        type_.value]]
                         .groupby([COUNTRY, DATE])
                         .sum())
        tabulated_data = filtered_data.pivot_table(columns=COUNTRY,
                                                   index=DATE,
                                                   values=type_.value)
        return tabulated_data

    def _get_time_series_for_country_days(
            self, type_: ValueType, countries: List[str], days: int) -> pd.DataFrame:

        time_series_data = self.data[type_].time_series

        df_countries = time_series_data[time_series_data[COUNTRY].isin(countries)]
        df_countries = (df_countries[[COUNTRY,
                                      DATE,
                                      type_.value]]
                        .groupby([COUNTRY, DATE],
                                 as_index=False)
                        .sum())
        start_dates = (df_countries[df_countries[type_.value] >= days]
                       .groupby("country", as_index=False)["date"]
                       .min())
        df_merged = pd.merge(df_countries, start_dates, on="country")
        df_merged["days"] = df_merged["date_x"] - df_merged["date_y"]

        tabulated_data = df_merged.pivot_table(columns=COUNTRY,
                                               index="days",
                                               values=type_.value)
        return tabulated_data

    def get_time_delta_for_country(self,
                                   type_: ValueType,
                                   countries: Union[str, Iterable[str]],
                                   index_since_: Optional[int] = 0,
                                   rolling: int = 1) -> pd.DataFrame:
        if isinstance(countries, str):
            countries = [countries]

        return (self._get_time_series_for_country_days(type_, countries, index_since_)
                .fillna(0)
                .diff()
                .rolling(rolling)
                .mean())
