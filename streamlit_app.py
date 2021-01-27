import numpy as np
import streamlit as st
from streamlit_folium import folium_static
import folium

st.header('Map')
m = folium.Map()
folium_static(m)

st.markdown("""---""")
st.header('Location Details')

st.markdown("""---""")
st.header('Scatterplot Exploration')
st.markdown("""---""")