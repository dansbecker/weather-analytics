# weather-analytics

Home of code supporting [this climate analysis dashboard](https://share.streamlit.io/dansbecker/weather-analytics/main).

Based on raw daily weather data described [here](https://docs.opendata.aws/noaa-ghcn-pds/readme.html).

The first level of munging happens in `/sagemaker_notebooks` notebooks.

The `download_data.sh` script downloads output of those notebooks, which is then the basis for the Streamlit app.
