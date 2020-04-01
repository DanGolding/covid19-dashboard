import matplotlib.pyplot as plt

from covid19_dashboard.data_adaptor import DataAdaptor, ValueType

data_adaptor = DataAdaptor()
# countries = ["US", "Italy", "South Africa", "United Kingdom"]
countries = ["US", "Italy", "United Kingdom"]
start = 10
data_country = data_adaptor.get_time_series_for_country(ValueType.DEATHS, countries, start)

fig, ax = plt.subplots()
ax.plot(data_country.index.days, data_country[countries])
ax.set_yscale("log")
ax.set_xlim([-1, data_country.index.days.max()])
ax.set_ylim([start, data_country[countries].max().max()])
plt.show()
