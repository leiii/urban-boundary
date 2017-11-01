#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Lei Dong

"""
本脚本将GeoTiff格式的文件，按band的value筛选后，以{(lon, lat): value}形式输出
More about GDAL library, see:
http://www.gdal.org/gdal_tutorial.html
https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html
"""

from osgeo import gdal, osr, ogr
import numpy as np
import sys


# open geotiff
try:
    dataset = gdal.Open("INPUT.tif")
except Exception as e:
    print e
    
    
# select tiff band
try:
    band_num = 1
    band = dataset.GetRasterBand(band_num) 
except Exception as e:
    print e

    
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


# 按一定band的阈值选择坐标点
def filter(data, thre):
    rst = {}
    for row in range(len(data)):
        for col in range(len(data[row])):
            lon = xOrigin + (col + 0.5) * pixelWidth #pixal center
            lat = yOrigin + (row + 0.5) * pixelHeight
            if data[row][col] > thre:
                rst[(row, col)] = [lon, lat, data[row][col]]
    return rst


# 每个选择出来的点，计算和周围一定距离阈值内的点的球面距离
def neighbor(rst, gird = 100):
    foo = {}
    for key in rst:
        originX = key[0] - grid
        originY = key[1] - grid
        extend_key = []
        for i in range(2 * grid + 1):
            extend_key.append((originX, originY))
            originX += 1
            originY += 1
        for j in extend_key:
            if j in rst:
                lon1, lat1, value1 = rst[key]
                lon2, lat2, value2 = rst[j]
                distance = haversine(lon1, lat1, lon2, lat2)
                if (key, j) not in foo and (j, key) not in foo:
                    foo[(key, j)] = [lon1, lat1, value1, lon2, lat2, value2, distance]
    return foo



def array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):
    array = array[::-1] # reverse array so the tif looks like the array
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()


# test
if __name__ == "__main__":
    rasterOrigin = (-123.25745,45.43013)
    pixelWidth = 10
    pixelHeight = 10
    newRasterfn = 'test.tif'
    array = np.array([[ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                      [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                      [ 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1],
                      [ 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1],
                      [ 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1],
                      [ 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1],
                      [ 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1],
                      [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                      [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                      [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
    array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array)
