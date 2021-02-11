import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from streamlit_folium import folium_static
import folium
from branca.colormap import linear, LinearColormap

st.write('**Next step: Use the real data**')
st.write('**Let user select time period**')

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

@st.cache
def read_base_file():
    station_stats = pd.read_csv('./data/station_stats.csv')
    station_stats['pct_precip_change'] = (100 * station_stats.slope_total_precip_pct.round(3))
    station_stats['slope_max_temp'] = station_stats['slope_max_temp'].round(2)
    station_stats['slope_min_temp'] = station_stats['slope_min_temp'].round(2)
    return station_stats

START_YEAR = 1980
END_YEAR = 2020
num_years = END_YEAR - START_YEAR


metric_descs = {'slope_max_temp': 'Annual change (degrees Celsius) in average daily high temp',
                'slope_min_temp': 'Annual change (degrees Celsius) in average daily low temp',
                'pct_precip_change': 'Annual percent change in precipitation',}

metric_units = {'slope_max_temp': '° / year',
                'slope_min_temp': '° / year',
                'pct_precip_change': '% / year',}


reverse_colormap = {'slope_max_temp': True,
                    'slope_min_temp': True,
                    'pct_precip_change': False}


    
@st.cache(hash_funcs={folium.folium.Map: lambda _: None}, allow_output_mutation=True)
def make_map(field_to_color_by):
    main_map = folium.Map()
    colormap = linear.RdYlBu_08.scale(station_stats[field_to_color_by].quantile(0.05),
                                      station_stats[field_to_color_by].quantile(0.95))
    if reverse_colormap[field_to_color_by]:
        colormap = LinearColormap(colors=list(reversed(colormap.colors)),
                                  vmin=colormap.vmin,
                                  vmax=colormap.vmax)
    colormap.add_to(main_map)
    metric_desc = metric_descs[field_to_color_by]
    metric_unit = metric_units[field_to_color_by]
    colormap.caption = metric_desc
    colormap.add_to(main_map)
    for _, city in station_stats.iterrows():
        sample_data = pd.DataFrame({'x': [1,2,3,4,5,6],
                                    'y': [5,4,3,4,5,6]})
        some_chart = alt.Chart(sample_data).mark_line().encode(
            alt.X('x'),
            alt.Y('y')
        ).to_json()

        icon_color = colormap(city[field_to_color_by])
        folium.CircleMarker(location=[city.lat, city.lon],
                    tooltip=f"{city.municipality}\n  value: {city[field_to_color_by]}{metric_unit}",
                    fill=True,
                    fill_color=icon_color,
                    color=None,
                    fill_opacity=0.7,
                    radius=5,
                    popup = folium.Popup(max_width=400).add_child(
                                            folium.features.VegaLite(some_chart, width=400, height=300)
                                            )
                    ).add_to(main_map)
    return main_map

station_stats = read_base_file()
# st.dataframe(station_stats)
st.header('Map')

metric_for_map = st.selectbox('Climate metric for map',
                              options=list(metric_descs.keys()),
                              index=0,
                              format_func=lambda m: metric_descs[m])
main_map = make_map(metric_for_map)

folium_static(main_map)

st.markdown("""---""")
st.header('Location Details')

st.markdown("""---""")
st.header('Scatterplot Exploration')
st.markdown("""---""")


