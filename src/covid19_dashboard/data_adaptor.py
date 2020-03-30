from enum import Enum
from typing import Optional, List, Union

import pandas as pd

DATA_URL = (r"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/"
            r"csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")


class ColumnNames(Enum):
    state = "state"
    country = "country"
    latitude = "latitude"
    longitude = "longitude"
    date = "date"
    infections = "infections"


class DataAdaptor:

    def __init__(self, data_path: Optional[str] = None):
        if not data_path:
            data_path = DATA_URL

        data_raw = pd.read_csv(data_path)
        column_names_old = data_raw.columns[:4].values
        column_names_new = [column_name.value for column_name in ColumnNames][:4]
        data_raw = data_raw.rename(
            columns={old: new for old, new in zip(column_names_old,column_names_new)})
        data_no_geo_coords = data_raw.drop(columns=[ColumnNames.latitude.value,
                                                    ColumnNames.longitude.value])

        self.time_series_data = data_no_geo_coords.melt(value_vars=data_no_geo_coords.columns[2:],
                                                        id_vars=data_no_geo_coords.columns[:2],
                                                        var_name=ColumnNames.date.value,
                                                        value_name=ColumnNames.infections.value)
        self.time_series_data[ColumnNames.date.value] = pd.to_datetime(
            self.time_series_data[ColumnNames.date.value])
        self.geo_data = data_raw.iloc[:, :4].drop_duplicates()

    def get_time_series_for_country(self, countries: Union[str, List[str]], index_since_num_infections: Optional[int] = 0):
        if isinstance(countries, str):
            countries = [countries]
        # countries = [country.title() for country in countries]

        if index_since_num_infections:
            return self._get_time_series_for_country_days(countries, index_since_num_infections)
        else:
            return self._get_time_series_for_country_by_date(countries)

    def _get_time_series_for_country_by_date(self, countries: List[str]):
        """Return a time series of total infections for specific countries

        :param countries: A list of country names
        :return:
        """
        filtered_data = self.time_series_data[
            self.time_series_data[ColumnNames.country.value].isin(countries)]
        filtered_data = (filtered_data[[ColumnNames.country.value,
                                        ColumnNames.date.value,
                                        ColumnNames.infections.value]]
                         .groupby([ColumnNames.country.value, ColumnNames.date.value])
                         .sum())
        tabulated_data = filtered_data.pivot_table(columns=ColumnNames.country.value,
                                                   index=ColumnNames.date.value,
                                                   values=ColumnNames.infections.value)
        return tabulated_data

    def _get_time_series_for_country_days(self, countries: List[str], days: int):

        df_countries = self.time_series_data[
            self.time_series_data[ColumnNames.country.value].isin(countries)]
        df_countries = (df_countries[[ColumnNames.country.value,
                                      ColumnNames.date.value,
                                      ColumnNames.infections.value]]
                        .groupby([ColumnNames.country.value, ColumnNames.date.value],
                                 as_index=False)
                        .sum())
        print(df_countries)
        start_dates = (df_countries[df_countries["infections"] >= 100]
                       .groupby("country", as_index=False)["date"]
                       .min())
        df_merged = pd.merge(df_countries, start_dates, on="country")
        df_merged["days"] = df_merged["date_x"] - df_merged["date_y"]

        tabulated_data = df_merged.pivot_table(columns=ColumnNames.country.value,
                                               index="days",
                                               values=ColumnNames.infections.value)
        return tabulated_data
