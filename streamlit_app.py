import pandas as pd
import streamlit as st
import altair as alt
from streamlit_folium import folium_static
import folium
from branca.colormap import linear, LinearColormap

st.header("Temporary Notes")
st.write("This is scratchwork. The goal is an interactive tool to see how climate has changed in different locations.")
st.write("Based on aggregations of raw daily weather data from: https://docs.opendata.aws/noaa-ghcn-pds/readme.html")

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

@st.cache
def get_annual_stats():
    raw_data = pd.read_parquet('./data/weather_1980_to_2020.parquet')
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



@st.cache(allow_output_mutation=True)
def make_city_graphs(allow_output_mutation=True):
    # Folium converts vegalite scatters to line graphs in an ugly way. So, make a graph
    # that looks good after the conversion, even if it looks different from standalone
    def make_one_city_map_graphs(annual_this_city, city_name, annual_data_field):
        graph = alt.Chart(annual_this_city, title=city_name).mark_line().encode(
            alt.X('year', scale=alt.Scale(zero=False), axis=alt.Axis(format="d")),
            alt.Y(annual_data_field, scale=alt.Scale(zero=False)),
        )
        return graph

    def make_one_city_standalone_graphs(annual_this_city, city_name, annual_data_field):
        graph = alt.Chart(annual_this_city, title=city_name).mark_point().encode(
            alt.X('year', scale=alt.Scale(zero=False), axis=alt.Axis(format="d")),
            alt.Y(annual_data_field, scale=alt.Scale(zero=False)),
        )
        return graph + graph.transform_regression('year', annual_data_field).mark_line()

    out = {'for_map': {},
           'standalone': {}}
    for _, city in station_stats.iterrows():
        annual_this_city = annual_stats.loc[annual_stats.station_id == city.station_id]
        city_name = city.municipality
        station_id = city.station_id
        out['for_map'][station_id] = {summary_stat: make_one_city_map_graphs(annual_this_city, city_name, annual_stat) 
                        for summary_stat, annual_stat in name_in_annual_data.items()}
        out['standalone'][city_name] = {annual_stat: make_one_city_standalone_graphs(annual_this_city, city_name, annual_stat) 
                        for summary_stat, annual_stat in name_in_annual_data.items()}
    return out

    
@st.cache(hash_funcs={folium.folium.Map: lambda _: None}, allow_output_mutation=True)
def make_map(field_to_color_by):
    main_map = folium.Map(location=(39, -77), zoom_start=1)
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
        icon_color = colormap(city[field_to_color_by])
        city_graph = city_graphs['for_map'][city.station_id][field_to_color_by]
        folium.CircleMarker(location=[city.lat, city.lon],
                    tooltip=f"{city.municipality}\n  value: {city[field_to_color_by]}{metric_unit}",
                    fill=True,
                    fill_color=icon_color,
                    color=None,
                    fill_opacity=0.7,
                    radius=5,
                    popup = folium.Popup().add_child(
                                            folium.features.VegaLite(city_graph)
                                            )
                    ).add_to(main_map)
    return main_map

annual_stats = get_annual_stats()
station_stats = read_base_file()
city_graphs = make_city_graphs()

st.header('Map')
st.write("Note: You can zoom in. Get the history for a location by clicking on it.")
st.write("**TODO:** Make sure we are showing all cities with available data.")
metric_for_map = st.selectbox('Climate metric for map',
                              options=list(metric_descs.keys()),
                              index=0,
                              format_func=lambda m: metric_descs[m])
main_map = make_map(metric_for_map)

folium_static(main_map)

st.markdown("""---""")
st.header('Single Location Focus')
region = st.selectbox("Region", sorted(station_stats.region.unique()), index=0)
city_name = st.selectbox("City", sorted(station_stats.loc[station_stats.region == region].municipality.unique()))
for graph_name, graph in city_graphs['standalone'][city_name].items():
    st.write(graph_name)
    st.write(graph)

st.markdown("""---""")
st.header('POSSIBLE TODO: Scatterplot Exploration')
st.write("""Select two variables (e.g. latitude vs temp change) and see scatterplot""")
st.write("""Variables include lat, lon, elevation, avg temp change over different time periods, annual % precip change, etc""")

st.header('POSSIBLE TODO: Look at Seasonal Results')
st.write('Allow user to specify they want results just for a specific season or calendar month. Those look different than annual averages')