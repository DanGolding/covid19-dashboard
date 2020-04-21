import altair as alt
import streamlit as st
from covid19_dashboard.charting import plot_data_since, plot_delta_since

from covid19_dashboard.data_adaptor import DataAdaptor, ValueType


@st.cache
def get_data():
    return DataAdaptor()


st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: 80%;
    }}
</style>
""",
        unsafe_allow_html=True,
    )

data_adaptor = get_data()

country_list = data_adaptor.countries
countries = st.multiselect(
    label='Countries', options=country_list, default=["US", "United Kingdom"])

start_infections = 100
chart_infections_total = plot_data_since(
    data_adaptor, ValueType.INFECTIONS, countries, start=start_infections)
chart_infections_daily = plot_delta_since(
    data_adaptor, ValueType.INFECTIONS, countries, start=start_infections, rolling=7)
start_deaths = 20
chart_deaths_total = plot_data_since(data_adaptor, ValueType.DEATHS, countries, start=start_deaths)
chart_deaths_daily = plot_delta_since(
    data_adaptor, ValueType.DEATHS, countries, start=start_deaths, rolling=7)

h_space = 80
v_space = 100
composite_chart = alt.vconcat(
    alt.hconcat(chart_infections_total, chart_infections_daily, spacing=h_space),
    alt.hconcat(chart_deaths_total, chart_deaths_daily, spacing=h_space),
    spacing=v_space,
    padding={"left": 100, "top": 20}
)
st.altair_chart(composite_chart)
