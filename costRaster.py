import ogr, gdal, osr
import numpy as np
from math import sqrt

def shp2array(inputfn,baseRasterfn):    
    outputfn = 'rasterized.tif'
    
    source_ds = ogr.Open(inputfn)
    source_layer = source_ds.GetLayer()
    
    raster = gdal.Open(baseRasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3] 
    pixelWidth = geotransform[1] 
    pixelHeight = geotransform[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize

    target_ds = gdal.GetDriverByName('GTiff').Create(outputfn, cols, rows, 1, gdal.GDT_Byte) 
    target_ds.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    band = target_ds.GetRasterBand(1)
    NoData_value = 255
    band.SetNoDataValue(NoData_value)
    gdal.RasterizeLayer(target_ds, [1], source_layer, burn_values=[0])   

    # Read as array
    array = band.ReadAsArray()
    return array
    
def pixelOffset2coord(xOffset,yOffset):
    raster = gdal.Open('rasterized.tif')
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    coordX = originX+pixelWidth*xOffset
    coordY = originY+pixelHeight*yOffset
    return coordX, coordY
    
def roadArray2coordDict(array):
    count = 0
    roadList = np.where(array == 0)
    roadListCoord = []
    for indexY in roadList[0]:
        indexX = roadList[1][count]
        Xcoord, Ycoord = pixelOffset2coord(indexX,indexY)
        coords = (Xcoord, Ycoord)
        roadListCoord.append(coords)
        count += 1
    return roadListCoord
    
def distance(coord0X,coord0Y,coord1):
    return sqrt((coord0X-coord1[0])**2+(coord0Y-coord1[1])**2)  
    
def nonRoadArray2coord(array, roadListCoord):
    distArray = (np.copy(array)).astype(float)
    count = 0
    nonRoadList = np.where(array != 0)
    for indexY in nonRoadList[0]:
        indexX = nonRoadList[1][count]
        nonRoadXcoord, nonRoadYcoord = pixelOffset2coord(indexX,indexY)
        minDist = min([distance(nonRoadXcoord,nonRoadYcoord,roadPoint) for roadPoint in roadListCoord])         
        distArray[indexY,indexX] = minDist
        count += 1   
    return distArray
    
def raster2array(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray()
    return array
    
def array2raster(newRasterfn,distArray):    
    raster = gdal.Open('rasterized.tif')
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(distArray)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(26913)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())  
    
if __name__ == '__main__':
    roads_fn = 'data/OSM/roads.shp'
    slope_fn = 'data/CSFS/Slope.tif'
    newRasterfn = 'data/CostSurface.tif'
    
    roadArray = shp2array(roads_fn, slope_fn)
    roadListCoord = roadArray2coordDict(roadArray)
    
    slopeArray = raster2array(slope_fn)
    skidDistArray = nonRoadArray2coord(roadArray,roadListCoord)
    
    costArray = 20.380512 + slopeArray*0.354856 + skidDistArray*0.006138
    array2raster(newRasterfn,costArray)

    