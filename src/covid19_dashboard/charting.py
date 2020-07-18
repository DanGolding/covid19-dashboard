from typing import Iterable, Optional

import altair as alt
import numpy as np

from covid19_dashboard.data_adaptor import DataAdaptor, ValueType


def plot_delta_since(data_adaptor: DataAdaptor,
                    type_: ValueType,
                    countries: Iterable[str],
                    start: Optional[int] = None,
                    rolling: int = 1,
                    width: Optional[int] = None,
                    height: Optional[int] = None) -> alt.Chart:

    source = (data_adaptor
              .get_time_delta_for_country(type_, countries, start, rolling)
              .reset_index()
              .melt('days', var_name="country", value_name=type_.value))
    source["days"] = source["days"].dt.days
    source[source.loc[:, type_.value] <= 0] = np.NAN
    if start:
        source = source[source["days"] >= 0]

    ylabel = f"{type_.value.title()} per day"
    if rolling > 1:
        ylabel += f" ({rolling} day moving average)"

    line = alt.Chart(source).mark_line(interpolate='basis').encode(
        x=alt.X('days:Q', title=f"Days since {start} {type_.value}",  axis=alt.Axis(grid=False)),
        # TODO: calc the max tickcounts by finding the log_10 of the data max range
        y=alt.Y(f'{type_.value}:Q', scale=alt.Scale(type="log"), title=ylabel, axis=alt.Axis(tickCount=5)),
        color='country:N'
    )

    chart = _plot_with_data_bar(source, line, type_, width, height)

    return chart


def plot_data_since(data_adaptor: DataAdaptor,
                    type_: ValueType,
                    countries: Iterable[str],
                    start: Optional[int] = None,
                    width: Optional[int] = None,
                    height: Optional[int] = None) -> alt.Chart:

    source = (data_adaptor
              .get_time_series_for_country(type_, countries, start)
              .reset_index()
              .melt('days', var_name="country", value_name=type_.value))
    source["days"] = source["days"].dt.days
    if start:
        source = source[source["days"] >= 0]

    line = alt.Chart(source).mark_line(interpolate='basis').encode(
        x=alt.X('days:Q', title=f"Days since {start} {type_.value}", axis=alt.Axis(grid=False)),
        y=alt.Y(f'{type_.value}:Q', scale=alt.Scale(type="log"), title=f"{type_.value.title()}", axis=alt.Axis(tickCount=5)),
        color='country:N'
    )

    chart = _plot_with_data_bar(source, line, type_, width, height)

    return chart


def _plot_with_data_bar(source: alt.Chart,
                        line: alt.Chart,
                        type_: ValueType,
                        width: Optional[int] = None,
                        height: Optional[int] = None) -> alt.Chart:

    width = 800 if width is None else width
    height = 400 if height is None else height

    # TODO: Add validation that the x and y series names are correct

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover', fields=['days'],
                            empty='none')

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
    text = line.mark_text(align='left', dx=5, dy=10).encode(
        text=alt.condition(nearest, f'{type_.value}:Q', alt.value(' '), format=".0f")
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
        width=width, height=height
    )

    return chart
