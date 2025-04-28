import requests
import pandas as pd

# Main feed URL
gbfs_url = "https://gbfs.divvybikes.com/gbfs/gbfs.json"
feeds = requests.get(gbfs_url).json()
feed_dict = {feed["name"]: feed["url"] for feed in feeds["data"]["en"]["feeds"]}

# Get URLs for station info and station status
station_info_url = feed_dict["station_information"]
station_status_url = feed_dict["station_status"]

# Download both
info = requests.get(station_info_url).json()
status = requests.get(station_status_url).json()

# Normalize and merge
info_df = pd.json_normalize(info["data"]["stations"])
status_df = pd.json_normalize(status["data"]["stations"])
df = pd.merge(info_df, status_df, on="station_id")

# Preview key columns
print(df[["station_id", "name", "lat", "lon", "num_bikes_available", "num_docks_available"]].head())
