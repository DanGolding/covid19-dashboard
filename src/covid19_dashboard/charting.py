from typing import Iterable, Optional

import altair as alt
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


def plot_data_since_altair(data_adaptor: DataAdaptor,
                           type_: ValueType,
                           countries: Iterable[str],
                           start: Optional[int] = None) -> alt.Chart:

    source = (data_adaptor
              .get_time_series_for_country(type_, countries, start)
              .reset_index()
              .melt('days', var_name="country", value_name=type_.value))
    source["days"] = source["days"].dt.days
    if start:
        source = source[source["days"] >= 0]

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover', fields=['days'],
                            empty='none')

    # The basic line
    line = alt.Chart(source).mark_line(interpolate='basis').encode(
        x='days:Q',
        # y=f'{type_.value}:Q',
        y=alt.Y(f'{type_.value}:Q', scale=alt.Scale(type="log")),
        color='country:N'
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(source).mark_point().encode(
        x='days:Q',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, f'{type_.value}:Q', alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(source).mark_rule(color='gray').encode(
        x='days:Q',
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    chart = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=600, height=300
    )

    return chart