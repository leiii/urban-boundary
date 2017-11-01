#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Lei Dong

"""
本脚本将GeoTiff格式的文件，按band的value筛选后，以{(lon, lat): value}形式输出
More about GDAL library, see:
http://www.gdal.org/gdal_tutorial.html
https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html
"""

import numpy as np
from osgeo import gdal

dataset = gdal.Open('SEN14adjv1.tif')

cols = dataset.RasterXSize
rows = dataset.RasterYSize
band = dataset.GetRasterBand(1) #选择数据通道
transform = dataset.GetGeoTransform()

# Transform the band value to array
data = band.ReadAsArray(0, 0, cols, rows)

xOrigin = transform[0] # top left x
yOrigin = transform[3] # top left y
pixelWidth = transform[1] # width pixal resolution
pixelHeight = transform[5] # hight pixal resolution (negative value)

print xOrigin, yOrigin, pixelWidth, pixelHeight


def filter(data, thre):
    rst = {}
    for row in range(len(data)):
        for col in range(len(data[row])):
            lon = xOrigin + (col + 0.5) * pixelWidth #pixal center
            lat = yOrigin + (row + 0.5) * pixelHeight
            if data[row][col] > thre:
                rst[(lon, lat)] = data[row][col]
    return rst
