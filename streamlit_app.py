import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import folium
from branca.colormap import linear

station_stats = pd.read_csv('station_stats.csv')
START_YEAR = 1980
END_YEAR = 2020
num_years = END_YEAR - START_YEAR
station_stats['pct_precip_change'] = (100 * ((1+station_stats.slope_total_precip_pct) ** num_years - 1)
                                     ).astype('int')
st.dataframe(station_stats)
st.header('Map')

main_map = folium.Map()

field_to_color_by = 'pct_precip_change'
colormap = linear.RdYlBu_08.scale(station_stats[field_to_color_by].quantile(0.05),
                                  station_stats[field_to_color_by].quantile(0.95))
colormap.add_to(main_map)
colormap.caption = field_to_color_by
colormap.add_to(main_map)
for _, city in station_stats.iterrows():
    icon_color = colormap(city[field_to_color_by])
    folium.CircleMarker(location=[city.lat, city.lon],
                  popup=f"{city.station_id}\n{city.municipality}\n{field_to_color_by}:{city[field_to_color_by]}%",
                        fill=True,
                        fill_color=icon_color,
                        color=None,
                        fill_opacity=0.7,
                        radius=5
                 ).add_to(main_map)

folium_static(main_map)

st.markdown("""---""")
st.header('Location Details')

st.markdown("""---""")
st.header('Scatterplot Exploration')
st.markdown("""---""")


