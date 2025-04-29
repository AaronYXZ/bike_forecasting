import streamlit as st  # Import Streamlit for creating web apps
import pandas as pd  # Import pandas for data manipulation
import datetime as dt  # Import datetime for handling date and time
from helper import get_dock_availability, get_marker_color, get_bike_availability, run_osrm , geocode  # Import custom utils functions
from helper import query_station
import folium  # Import folium for creating interactive maps
from streamlit_folium import folium_static  # Import folium_static to render Folium maps in Streamlit


# Streamlit app setup
st.title('Chicage Bike Share Station Status')  # Set the title of the app
st.markdown('This dashboard tracks bike availability at each bike share station in Chicage.')  # Add a description

gbfs_url = "https://gbfs.divvybikes.com/gbfs/gbfs.json"
CHICAGO = [41.85003000, -87.65005000]  # Coordinates for Chicago
# Fetch data for initial visualization
data = query_station(gbfs_url)  # Join the status data with the location data

# Display initial metrics
col1, col2, col3 = st.columns(3)  # Create three columns for metrics
with col1:
    st.metric(label="Bikes Available Now", value=sum(data['num_bikes_available']))  # Display total number of bikes available
    st.metric(label="E-Bikes Available Now", value=sum(data["num_ebikes_available"]))  # Display total number of e-bikes available
with col2:
    st.metric(label="Stations w Available Bikes", value=len(data[data['num_bikes_available'] > 0]))  # Display number of stations with available bikes
    st.metric(label="Stations w Available E-Bikes", value=len(data[data['num_ebikes_available'] > 0]))  # Display number of stations with available e-bikes
with col3:
    st.metric(label="Stations w Empty Docks", value=len(data[data['num_docks_available'] > 0]))  # Display number of stations with empty docks

# Track metrics for delta calculation
deltas = [
    sum(data['num_bikes_available']),
    sum(data["num_ebikes_available"]),
    len(data[data['num_bikes_available'] > 0]),
    len(data[data['num_ebikes_available'] > 0]),
    len(data[data['num_docks_available'] > 0])
]

# Initialize variables for user input and state
iamhere = 0
iamhere_return = 0
findmeabike = False
findmeadock = False
input_bike_modes = []

# Add sidebar selection for user inputs
with st.sidebar:
    bike_method = st.selectbox("Are you looking to rent or return a bike?", ("Rent", "Return"))  # Selection box for rent or return
    if bike_method == "Rent":
        input_bike_modes = st.multiselect("What kind of bikes are you looking to rent?", ["ebike", "mechanical"])  # Multi-select box for bike types
        st.subheader('Where are you located?')
        input_street = st.text_input("Street", "")  # Text input for street
        input_city = st.text_input("City", "Chicago")  # Text input for city
        input_country = st.text_input("Country", "United States")  # Text input for country
        drive = st.checkbox("I'm driving there.")  # Checkbox for driving option
        findmeabike = st.button("Find me a bike!", type="primary")  # Button to find a bike
        if findmeabike:
            if input_street != "":
                iamhere = geocode(input_street + " " + input_city + " " + input_country)  # Geocode the input address
                if iamhere == '':
                    st.subheader(':red[Input address not valid!]')  # Display error if address is invalid
            else:
                st.subheader(':red[Please input your location.]')  # Prompt user to input location if missing
    elif bike_method == "Return":
        st.subheader('Where are you located?')
        input_street_return = st.text_input("Street", "")  # Text input for street for return
        input_city_return = st.text_input("City", "Chicage")  # Text input for city for return
        input_country_return = st.text_input("Country", "United States")  # Text input for country for return
        findmeadock = st.button("Find me a dock!", type="primary")  # Button to find a dock
        if findmeadock:
            if input_street_return != "":
                iamhere_return = geocode(input_street_return + " " + input_city_return + " " + input_country_return)  # Geocode the return address
                if iamhere_return == '':
                    st.subheader(':red[Input address not valid!]')  # Display error if address is invalid
            else:
                st.subheader(':red[Please input your location.]')  # Prompt user to input location if missing

def create_map(center, data, marker_color_func, popup_template, zoom_start=13):
    """
    Create a Folium map with bike station markers.
    """
    m = folium.Map(location=center, zoom_start=zoom_start, tiles='cartodbpositron')
    for _, row in data.iterrows():
        marker_color = marker_color_func(row)
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=2,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_template.format(**row), max_width=300)
        ).add_to(m)
    return m

def add_user_and_station_markers(map_obj, user_location, station_location, station_popup, user_popup="You are here."):
    """
    Add user and station markers to the map.
    """
    folium.Marker(
        location=user_location,
        popup=user_popup,
        icon=folium.Icon(color="blue", icon="person", prefix="fa")
    ).add_to(map_obj)
    folium.Marker(
        location=station_location,
        popup=station_popup,
        icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
    ).add_to(map_obj)

def display_route(map_obj, coordinates, duration):
    """
    Add a route polyline to the map and display travel time.
    """
    folium.PolyLine(
        locations=coordinates,
        color="blue",
        weight=5,
        tooltip=f"It'll take you {duration} to get here."
    ).add_to(map_obj)
    return duration

# Popup template for stations
popup_template = (
    "Station ID: {station_id}<br>"
    "Total Bikes Available: {total_num_bikes_available}<br>"
    "Mechanical Bike Available: {num_bikes_available}<br>"
    "eBike Available: {num_ebikes_available}"
)

# Initial map setup
if bike_method == "Return" and not findmeadock:
    center = CHICAGO
    m = create_map(center, data, lambda row: get_marker_color(row['total_num_bikes_available']), popup_template)
    folium_static(m)

if bike_method == "Rent" and not findmeabike:
    center =CHICAGO
    m = create_map(center, data, lambda row: get_marker_color(row['total_num_bikes_available']), popup_template)
    folium_static(m)

# Logic for finding a bike
if findmeabike and input_street and iamhere:
    chosen_station = get_bike_availability(iamhere, data, input_bike_modes)
    center = iamhere
    m1 = create_map(center, data, lambda row: get_marker_color(row['total_num_bikes_available']), popup_template, zoom_start=16)
    add_user_and_station_markers(m1, iamhere, (chosen_station[1], chosen_station[2]), "Rent your bike here.")
    coordinates, duration = run_osrm(chosen_station, iamhere)
    travel_time = display_route(m1, coordinates, duration)
    folium_static(m1)
    with col3:
        st.metric(label=":green[Travel Time (min)]", value=travel_time)

# Logic for finding a dock
if findmeadock and input_street_return and iamhere_return:
    chosen_station = get_dock_availability(iamhere_return, data)
    center = iamhere_return
    m1 = create_map(center, data, lambda row: get_marker_color(row['num_bikes_available']), popup_template, zoom_start=16)
    add_user_and_station_markers(m1, iamhere_return, (chosen_station[1], chosen_station[2]), "Return your bike here.")
    coordinates, duration = run_osrm(chosen_station, iamhere_return)
    travel_time = display_route(m1, coordinates, duration)
    folium_static(m1)
    with col3:
        st.metric(label=":green[Travel Time (min)]", value=travel_time)