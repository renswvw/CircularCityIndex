import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import rasterstats
from rasterio.plot import show, show_hist
from datetime import datetime


# Get the current working directory
#cwd = os.getcwd()
cwd = 'c:/Users/rensw/OneDrive - Universiteit Utrecht/GIMA/Thesis - Buitenland/Thesis/Data/Raw_data/ECR5'

# Print the current working directory
print("Current working directory: {0}".format(cwd))

# Source of script
# https://www.youtube.com/watch?v=VIr-pejky6E&ab_channel=GeoDeltaLabs

# create new folders
#os.makedirs(cwd + '/interim/ECR5_interimdata_07112022')

# create path 
path_rawdata = cwd + '/raw/AQ_2019_shape-files/NOx/interpolated-values/geoTIFF/'
raw_rasterfile = path_rawdata + 'nox_avg19.tif'
print(raw_rasterfile)

#replace nodata value raster
interim_rasterfile = cwd + '/interim/' + "interim_NOx_avg19.tif"
with rasterio.open(raw_rasterfile, "r+") as src:
    src.nodata = 0 # set the nodata value
    profile = src.profile
    profile.update(
            dtype=rasterio.uint8,
            compress='lzw'
    )

    with rasterio.open(interim_rasterfile, 'w',  **profile) as dst:
        for i in range(1, src.count + 1):
            band = src.read(i)
            # band = np.where(band!=1,0,band) # if value is not equal to 1 assign no data value i.e. 0
            band = np.where(band==0,0,band) # for completeness
            dst.write(band,i)

# read shapefile boundaries Spain Mainland
shapefile = 'C:/Users/rensw/OneDrive - Universiteit Utrecht/GIMA/Thesis - Buitenland/Thesis/Data/Raw_data/Administrative_Boundaries/interim/AdministrativeBoundaries_Total_InterimData_14112022.shp'
boundaries = gpd.read_file(shapefile)
boundaries.plot()
print(boundaries.crs)

# read rasterfile NOx
rf = rasterio.open(interim_rasterfile)
show(rf)
    
# check interim raster file
print('width =',(rf.width))
print('height =',(rf.height))
print('BoundingBox =',(rf.bounds))
print('CRS =',(rf.crs))

# change projection
CRS = rf.crs
boundaries = boundaries.to_crs(CRS)
    
# creating platform to plot graphs on -- plotting rasterfile and shapefile combined
fig, ax = plt.subplots(1,1)
show(rf, ax=ax, title = 'NOx by administrative districs')
boundaries.plot(ax=ax, facecolor='None', edgecolor = 'yellow')
plt.show()

# Adding histogram to plot
fig, (ax1, ax2) = plt.subplots(1,2, figsize = (10,4))
show(rf, ax=ax1, title = 'NOx by administrative districs')
boundaries.plot(ax=ax1, facecolor='None', edgecolor = 'yellow')
show_hist(rf, title = 'Histogram', ax=ax2)
plt.show()

# Extract raster values to a numpy nd array
NOx_array = rf.read(1)
type(NOx_array)

# Transform raster
affine = rf.transform

# Get metadata
metadata = rf.meta
print(metadata)
print(rf.nodata)
print(rf.crs)

# Calculate zonal stats
average_NOx = rasterstats.zonal_stats(boundaries, NOx_array, affine = affine, stats = ['mean'], geojson_out = True)
print(average_NOx)

# Extracting NOx values per municipality
mean_NOx = []
i = 0

while i < len(average_NOx):
    mean_NOx.append(average_NOx[i]['properties'])
    print(i)
    i = i + 1

# Extracting data to dataframe
df = pd.DataFrame(mean_NOx)
print(df)

# Rename column headers
df['Municipality'] = df['Municipali']
df['Average_NOx_value'] = df['mean']

# Select only the columns with municipality name and value
df = df[['Municipality','Average_NOx_value']]
print(df)

# Data cleaning of useless values
df['Average_NOx_value'] = df['Average_NOx_value'].replace(0, np.nan)
df['Average_NOx_value'] = df['Average_NOx_value'].fillna('NoData')
print(df)

# exports the dataframe into csv file with
folder = 'interim'
file_name = 'ECR5_interimdata'
date = datetime.now().strftime("%d%m%Y")
data_format = '.csv'

export_name = '/' + folder + '/' + file_name + '_' + date + data_format

df.to_csv(cwd + export_name, index=False)

# exports the dataframe into excel file with
folder = 'interim'
file_name = 'ECR5_interimdata' 
date = datetime.now().strftime("%d%m%Y")
data_format = '.xlsx'

export_name = '/' + folder + '/' + file_name + '_' + date + data_format

df.to_excel(cwd + export_name, index=False)