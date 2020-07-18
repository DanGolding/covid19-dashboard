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
        max-width: 100%;
    }}
</style>
""",
        unsafe_allow_html=True,
    )

data_adaptor = get_data()

country_list = data_adaptor.countries
countries = st.sidebar.multiselect(
    label='Countries', options=country_list, default=["US", "United Kingdom"])

start_infections = st.sidebar.slider(
    "Start charts since number of infections:", min_value=0, max_value=5_000, value=100, step=10)
start_deaths = st.sidebar.slider(
    "Start charts since number of deaths:", min_value=0, max_value=1_000, value=20, step=5)
rolling = st.sidebar.slider(
    "Rolling average window:", min_value=0, max_value=90, value=7, step=1)


width = st.sidebar.number_input("Chart width", value=800)
height = st.sidebar.number_input("Chart height", value=400)


chart_infections_total = plot_data_since(
    data_adaptor, ValueType.INFECTIONS, countries, start=start_infections, width=width, height=height)
chart_infections_daily = plot_delta_since(
    data_adaptor, ValueType.INFECTIONS, countries, start=start_infections, rolling=rolling, width=width, height=height)
chart_deaths_total = plot_data_since(
    data_adaptor, ValueType.DEATHS, countries, start=start_deaths, width=width, height=height)
chart_deaths_daily = plot_delta_since(
    data_adaptor, ValueType.DEATHS, countries, start=start_deaths, rolling=rolling, width=width, height=height)

h_space = 80
v_space = 80
composite_chart = alt.vconcat(
    alt.hconcat(chart_infections_total, chart_infections_daily, spacing=h_space),
    alt.hconcat(chart_deaths_total, chart_deaths_daily, spacing=h_space),
    spacing=v_space,
    padding={"left": 100, "top": 20}
)
st.altair_chart(composite_chart)