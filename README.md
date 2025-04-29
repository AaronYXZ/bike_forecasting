# Chicago Bike Share Live Tracker

This is a **Streamlit web application** that displays real-time bike and dock availability at Divvy stations across Chicago, using the official GBFS data feed.

## Live Features

- View available bikes and e-bikes across the city
- Find the nearest station to **rent** or **return** a bike based on your current address
- Interactive map with live updates and color-coded station availability
- Driving directions and travel time estimates via OSRM routing

## Tech Stack

- [Streamlit](https://streamlit.io/) for frontend interface
- [Folium](https://python-visualization.github.io/folium/) for interactive maps
- [GBFS Feed](https://gbfs.divvybikes.com/gbfs/gbfs.json) for real-time station data
- [OpenStreetMap + OSRM](http://project-osrm.org/) for routing
- [Geopy](https://geopy.readthedocs.io/) for geocoding and distance calculation

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
