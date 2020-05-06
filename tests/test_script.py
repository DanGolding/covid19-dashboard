from typing import Iterable, Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes._subplots import Axes

from covid19_dashboard.data_adaptor import DataAdaptor, ValueType


def plot_data_since(data_adaptor: DataAdaptor,
                    type_: ValueType,
                    countries: Iterable[str],
                    ax: Axes,
                    start: Optional[int] = None,
                    legend: bool = False) -> None:

    data_country = data_adaptor.get_time_series_for_country(type_, countries, start)

    time_data = data_country.index.days if start else data_country.index
    ax.plot(time_data, data_country[countries])
    if legend:
        ax.legend(countries)
    ax.set_yscale("log")
    if start:
        ax.set_xlim(-1.0, data_country.index.days.max())
    ax.set_ylim(start, data_country.max().max())
    ax.set_ylabel(type_.value)
    if start:
        ax.set_xlabel(f"Days since {start} {type_.value}")
    else:
        ax.set_xlabel("Date")


def plot_delta_since(data_adaptor: DataAdaptor,
                     type_: ValueType,
                     countries: Iterable[str],
                     ax: Axes,
                     rolling: int = 1,
                     start: Optional[int] = None,
                     legend: bool = False) -> None:

    data_country = data_adaptor.get_time_delta_for_country(type_, countries, start, rolling)
    data_country[data_country <= 0] = np.NAN
    if start:
        data_country = data_country[data_country.index.days >= 0]

    time_data = data_country.index.days if start else data_country.index
    ax.plot(time_data, data_country[countries])
    if legend:
        ax.legend(countries)
    ax.set_yscale("log")
    ax.set_ylim(data_country.min().min(), data_country.max().max())
    ylabel = f"{type_.value} per day"
    if rolling > 1:
        ylabel += f" ({rolling} day moving average)"
    ax.set_ylabel(ylabel)
    if start:
        ax.set_xlabel(f"Days since {start} {type_.value}")
    else:
        ax.set_xlabel("Date")


data_adaptor = DataAdaptor()
countries = ["US", "Italy", "United Kingdom", "Spain", "Netherlands", "Israel", "Sweden"]

fig, ax = plt.subplots(1, 2)

plot_data_since(data_adaptor, ValueType.DEATHS, countries, ax[0], start=100, legend=True)
plot_delta_since(data_adaptor, ValueType.DEATHS, countries, ax[1], rolling=7, start=100, legend=True)

plt.tight_layout()
plt.show()
