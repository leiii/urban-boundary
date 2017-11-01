#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Lei Dong

"""
本脚本将GeoTiff格式的文件，按band的value筛选后，以{(lon, lat): value}形式输出
More about GDAL library, see:
http://www.gdal.org/gdal_tutorial.html
https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html
"""

from osgeo import gdal
import sys
# this allows GDAL to throw Python Exceptions
gdal.UserExceptions()


# open geotiff
try:
    dataset = gdal.Open("INPUT.tif")
except RuntimeError, e:
    print 'Unable to open INPUT.tif'
    print e
    sys.exit(1)
    
    
# select tiff band
try:
    band_num = 1
    band = dataset.GetRasterBand(band_num) 
except RuntimeError, e:
    print 'Band (% i) not found' % band_num
    print e
    sys.exit(1)

    
# get coord information
transform = dataset.GetGeoTransform()
xOrigin = transform[0] # top left x
yOrigin = transform[3] # top left y
pixelWidth = transform[1] # width pixal resolution
pixelHeight = transform[5] # hight pixal resolution (negative value)
print xOrigin, yOrigin, pixelWidth, pixelHeight


# Transform the band value to array
cols = dataset.RasterXSize
rows = dataset.RasterYSize
data = band.ReadAsArray(0, 0, cols, rows)

def filter(data, thre):
    rst = {}
    for row in range(len(data)):
        for col in range(len(data[row])):
            lon = xOrigin + (col + 0.5) * pixelWidth #pixal center
            lat = yOrigin + (row + 0.5) * pixelHeight
            if data[row][col] > thre:
                rst[(lon, lat)] = data[row][col]
    return rst
