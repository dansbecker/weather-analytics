import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from streamlit_folium import folium_static
import folium
from branca.colormap import linear, LinearColormap

st.write('**Let user select time period**')

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

@st.cache
def get_annual_stats():
    raw_data = pd.read_parquet('./data/weather_1970_to_2020.parquet')
    raw_data['date'] = pd.to_datetime(raw_data.date)
    raw_data['year'] = raw_data.date.dt.year
    annual_stats = raw_data.fillna(0).groupby(['station_id', 'year']).agg(
                            {'max_temp_c': ['mean'],
                            'min_temp_c': ['mean'],
                            'precip_mm': ['sum']}
    ).reset_index()
    annual_stats.columns = ['station_id', 'year', 'max_temp_c', 'min_temp_c', 'precip_mm']
    return annual_stats

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

name_in_annual_data = {'slope_max_temp': 'max_temp_c',
                       'slope_min_temp': 'min_temp_c',
                       'pct_precip_change': 'precip_mm',}


reverse_colormap = {'slope_max_temp': True,
                    'slope_min_temp': True,
                    'pct_precip_change': False}


    
@st.cache(hash_funcs={folium.folium.Map: lambda _: None}, allow_output_mutation=True)
def make_map(field_to_color_by):
    annual_data_field = name_in_annual_data[field_to_color_by]
    city_plot_width = 200
    city_plot_height = 200
    main_map = folium.Map(width=800, height=500, zoom_start=3)
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
        annual_this_city = annual_stats.loc[annual_stats.station_id == city.station_id]
        scatter = alt.Chart(annual_this_city).mark_point().encode(
            alt.X('year', scale=alt.Scale(zero=False), axis=alt.Axis(format="d")),
            alt.Y(annual_data_field, scale=alt.Scale(zero=False))
        )

        full_chart = scatter + scatter.transform_regression('year', annual_data_field).mark_line()
        icon_color = colormap(city[field_to_color_by])
        folium.CircleMarker(location=[city.lat, city.lon],
                    tooltip=f"{city.municipality}\n  value: {city[field_to_color_by]}{metric_unit}",
                    fill=True,
                    fill_color=icon_color,
                    color=None,
                    fill_opacity=0.7,
                    radius=5,
                    popup = folium.Popup().add_child(
                                            folium.features.VegaLite(full_chart.to_json(),
                                                                     width=city_plot_width + 50,
                                                                     height=city_plot_height + 50
                                                                     )
                                            )
                    ).add_to(main_map)
    return main_map

annual_stats = get_annual_stats()
station_stats = read_base_file()

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


