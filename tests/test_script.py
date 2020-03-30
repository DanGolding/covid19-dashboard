import matplotlib.pyplot as plt

from covid19_dashboard.data_adaptor import DataAdaptor

data_adaptor = DataAdaptor()
countries = ["US", "Italy", "South Africa", "United Kingdom"]
data_country = data_adaptor.get_time_series_for_country(countries, 100)

fig, ax = plt.subplots()
ax.plot(data_country.index.days, data_country[countries])
ax.set_yscale("log")
ax.set_xlim([-1, data_country.index.days.max()])
ax.set_ylim([100, data_country[countries].max().max()])
plt.show()
