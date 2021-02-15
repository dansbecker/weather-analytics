#!/bin/bash
curl https://weather-bucket.s3-us-west-1.amazonaws.com/explore_output/station_stats.csv > data/station_stats.csv
curl https://weather-bucket.s3-us-west-1.amazonaws.com/data/city_locations.csv > data/city_locations.csv
curl https://weather-bucket.s3-us-west-1.amazonaws.com/weather_munge_output/weather_1970_to_2020.parquet > data/weather_1970_to_2020.parquet
curl https://weather-bucket.s3-us-west-1.amazonaws.com/weather_munge_output/weather_1980_to_2020.parquet > data/weather_1980_to_2020.parquet
curl https://weather-bucket.s3-us-west-1.amazonaws.com/weather_munge_output/weather_1990_to_2020.parquet > data/weather_1990_to_2020.parquet
ls -al data
