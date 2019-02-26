#import folium - lib for creating maps
import folium
#import pandas for data parsing
import pandas as pd
from folium.plugins import MarkerCluster

#load data
data = pd.read_csv("Volcanoes_USA.txt")
lat = data['LAT']
lon = data['LON']
elevation = data['ELEV']

#Function to change marker color
def color_change(elev):
    if elev<=1000:
        return ('green')
    elif 1000<elev<=3000:
        return ('orange')
    else:
        return ('red')


#crete simple map
map = folium.Map(location=[37.296933, -121.9574983], zoom_start=4, tiles="CartoDB dark_matter")

#create marker_cluster
marker_cluster = MarkerCluster().add_to(map)

#add some markers on my map
for lat, lon, elevation in zip(lat, lon, elevation):
    folium.CircleMarker(location=[lat, lon], radius=6, popup=str(elevation)+" m", fill_color=color_change(elevation), color="green", fill_opacity = 0.9).add_to(marker_cluster)

#saving map to html file

map.save("map1.html")
