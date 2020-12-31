import pandas as pd
import json
import math
import plotly.express as px
import numpy as np
from sklearn import neighbors

"""
-was unable to pip install scikit-learn within the Udemy_PythonDSMLBootcamp venv
-had to re-create another venv thru anaconda to install, then
-remade venv in PyCharm, selected 'inheriting global packages' option, and then worked as intended

-ran into memoryError when running code thru jupyter notebook/PyCharm when
-geojson file too large
"""
# pip list

# 1. nyczipcodetabulationareas.geojson
# 2. pluto_ziponly.geojson
nycmap = json.load(open("nyczipcodetabulationareas.geojson"))
# nycmap

zips = pd.read_csv('us-zip-code-latitude-and-longitude_ny.csv', usecols=['Zip', 'Latitude', 'Longitude'])
zips['Latitude'] = zips['Latitude'].apply(func=math.radians)
zips['Longitude'] = zips['Longitude'].apply(func=math.radians)
zips['Coordinates'] = list(zip(zips['Latitude'], zips['Longitude']))
# zips

zips.reset_index(inplace=True)
# zips
# zips['Zip']
# zips['Zip'][2276]

# load zip code data into BallTree
zipcoords = np.asarray(list(zips['Coordinates']))
tree = neighbors.BallTree(zipcoords, metric='haversine')
# tree

# load airbnb lodging data from csv file
df = pd.read_csv('AB_NYC_2019_with_borocodes.csv')
# df

# convert coordinates to radians, create coord. pairs
df['latitude'] = df['latitude'].apply(func=math.radians)
df['longitude'] = df['longitude'].apply(func=math.radians)
df['coord'] = list(zip(df['latitude'], df['longitude']))
# df

# query BallTree and save results back into dataframe
# querying airbnb locations against saved zip codes within BallTree..
# ..to determine the closest zip code to assign to each airbnb
bnbcoords = np.asarray(list(df['coord']))
dist, zipcode_index = tree.query(X=bnbcoords, k=1)
df['dist'] = dist
df['dist'] = df['dist'].apply(lambda x: x * 3960)
# 3960 is radius of Earth in miles, converting dist to miles

df['zipcode_index'] = zipcode_index
# df

mapping = dict(zips[['index', 'Zip']].values)
# mapping

df['zip_code'] = df.zipcode_index.map(mapping)
# df

# aggregate avg price within df by zip code
price_by_zip = df.groupby('zip_code')['price'].mean()
df2 = price_by_zip.to_frame().reset_index()
# df2.rename(columns = {'zip_code':'new_zip_code'}, inplace = True)
# df2.drop('zip_code', axis='1')
# df2

# choropleth map using plotly express
# px.choropleth for outline choropleth map
# px.choropleth_mapbox for choropleth tile map
fig = px.choropleth(df2,
                    geojson=nycmap,
                    color="price",
                    locations="zip_code",
                    # postalCode for nyczipcodetabulationareas.geojson,
                    # zipcode for pluto_ziponly.geojson
                    featureidkey="properties.postalCode",
                    projection="mercator"
                    )
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()

# try committing geojson files to mapshaper to view what map looks like
