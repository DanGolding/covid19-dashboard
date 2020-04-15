import streamlit as st
import matplotlib.pyplot as plt
from covid19_dashboard.charting import plot_data_since, plot_delta_since, plot_data_since_altair

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

# country_list = ["US", "Italy", "United Kingdom", "Spain", "Netherlands", "Israel", "Sweden"]
country_list = data_adaptor.countries
countries = st.multiselect(
    label='Countries', options=country_list, default=["US", "United Kingdom"])

chart = plot_data_since_altair(data_adaptor, ValueType.INFECTIONS, countries, start=100)
st.write(chart)
