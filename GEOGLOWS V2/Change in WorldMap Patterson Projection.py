import geopandas as gpd
from pyproj import Proj,Transformer
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import box
import pandas as pd

# Load the shapefile
shapefile_path = '/path to your/Shapefile/simplified_continent_shapefile.shp'
gdf = gpd.read_file(shapefile_path)

# Load and process data
data = pd.read_csv('path to your csv file with all the metric.csv')

data['nse_v1'] = pd.to_numeric(data['nse_v1'], errors='coerce') #Adjust column name 
data['nse_v2'] = pd.to_numeric(data['nse_v2'], errors='coerce') #Adjust column name 

epsilon = 1e-10
data['percentage_diff_nse'] = 100 * (data['nse_v2'] - data['nse_v1']) / (data['nse_v1'].abs() + epsilon)

tolerance = 10
data['category_nse'] = pd.cut(
    data['percentage_diff_nse'],
    bins=[-float('inf'), -tolerance, tolerance, float('inf')],
    labels=['Decrease', 'No Difference', 'Improvement']
)

data_improvement = data[data['category_nse'] == 'Improvement']
data_no_difference = data[data['category_nse'] == 'No Difference']
data_decrease = data[data['category_nse'] == 'Decrease']

antarctica_box = box(-168, -55, 180, 90)
bbox_antarctica = gpd.GeoDataFrame(geometry=[antarctica_box], crs='EPSG:4326')

#Clip Antartica
bbox_antarctica = bbox_antarctica.to_crs(gdf.crs)
world = gpd.clip(gdf, bbox_antarctica)

# 4326 to Patterson projection
wgs84 = Proj(proj='latlong', datum='WGS84')
patterson = Proj(proj='patterson', lon_0=12)
transformer = Transformer.from_proj(wgs84, patterson)

# Transform the world shapefile coordinates to the Patterson projection
world = world.to_crs(patterson.srs)

# Plot each subset as before
fig, axs = plt.subplots(3, 1, figsize=(8, 9))
fig.subplots_adjust(hspace=0.01, top=0.95, bottom=0.05)

# Function to plot each subset of data using the transformer
def plot_data(ax, data, color, label, axis):
    x, y = transformer.transform(data['longitude'].values, data['latitude'].values)
    ax.scatter(x, y, color=color, s=2, edgecolor='black', linewidth=0.1)
    ax.text(0.02, 0.05, label, va='bottom', ha='left', transform=ax.transAxes, fontsize=8)
    ax.text(-0.001, 0.5, axis, va='center', ha='right', rotation='vertical', transform=ax.transAxes, fontsize=8)

# Plot each subset
for ax, (data_subset, color, label) in zip(axs, [
    (data_improvement, 'green', "Improvement"),
    (data_no_difference, 'blue', "No Difference"),
    (data_decrease, 'red', "Decrease")
]):
    # Set bluish color outside the shapefile
    ax.set_facecolor('lightblue')
    world.plot(ax=ax, color='beige', edgecolor='black', linewidth=0.5)
    plot_data(ax, data_subset, color, label, f"n = {len(data_subset)}")
    ax.set_xlim([-2e7, 2e7])
    ax.set_ylim([-0.7e7, 1.1e7])
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])

# Set the overall title
plt.suptitle(r'Changes in NSE', fontsize=12, x=0.5, y=0.972, ha='center', va='top')
plt.savefig('path to save the plot.png', dpi=1800, bbox_inches='tight')  
plt.show()
