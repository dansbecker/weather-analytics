# weather-analytics

This repo is the code for [this climate analysis dashboard](https://share.streamlit.io/dansbecker/weather-analytics/main). It's a quick-and-dirty project to satisfy personal curiosity, so it isn't well documented. If you find it interesting, drop me a note, issue or PR and I'll be thrilled to connect.

It's based on this raw [daily weather data](https://docs.opendata.aws/noaa-ghcn-pds/readme.html).

It starts with ~100GB of data, so the first level of munging happened in `/sagemaker_notebooks` notebooks.

The`download_data.sh` script downloads output of those notebooks, which is then the basis for the Streamlit app.
