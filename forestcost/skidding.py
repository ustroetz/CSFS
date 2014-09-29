from osgeo import ogr, gdal, osr
import os
import numpy as np
import tempfile
import requests
import json


def createQuaterCentroids(stand_wkt):
    '''
    This function splits the stand in four quater and returns the centroids of the four split quaters
    '''
    
    geom_poly = ogr.CreateGeometryFromWkt(stand_wkt)

    # Create 4 squares polygons
    geom_poly_envelope = geom_poly.GetEnvelope()
    minX = geom_poly_envelope[0] 
    minY = geom_poly_envelope[2] 
    maxX = geom_poly_envelope[1] 
    maxY = geom_poly_envelope[3]

    '''
    coord0----coord1----coord2
    |           |           |
    |           |           |
    coord3----coord4----coord5
    |           |           |
    |           |           |
    coord6----coord7----coord8
    '''
    coord0 = minX, maxY
    coord1 = minX+(maxX-minX)/2, maxY
    coord2 = maxX, maxY
    coord3 = minX, minY+(maxY-minY)/2
    coord4 = minX+(maxX-minX)/2, minY+(maxY-minY)/2
    coord5 = maxX, minY+(maxY-minY)/2
    coord6 = minX, minY
    coord7 = minX+(maxX-minX)/2, minY
    coord8 = maxX, minY

    ringTopLeft = ogr.Geometry(ogr.wkbLinearRing)
    ringTopLeft.AddPoint_2D(*coord0)
    ringTopLeft.AddPoint_2D(*coord1)
    ringTopLeft.AddPoint_2D(*coord4)
    ringTopLeft.AddPoint_2D(*coord3)
    ringTopLeft.AddPoint_2D(*coord0)
    polyTopLeft = ogr.Geometry(ogr.wkbPolygon)
    polyTopLeft.AddGeometry(ringTopLeft)

    ringTopRight = ogr.Geometry(ogr.wkbLinearRing)
    ringTopRight.AddPoint_2D(*coord1)
    ringTopRight.AddPoint_2D(*coord2)
    ringTopRight.AddPoint_2D(*coord5)
    ringTopRight.AddPoint_2D(*coord4)
    ringTopRight.AddPoint_2D(*coord1)
    polyTopRight = ogr.Geometry(ogr.wkbPolygon)
    polyTopRight.AddGeometry(ringTopRight)

    ringBottomLeft = ogr.Geometry(ogr.wkbLinearRing)
    ringBottomLeft.AddPoint_2D(*coord3)
    ringBottomLeft.AddPoint_2D(*coord4)
    ringBottomLeft.AddPoint_2D(*coord7)
    ringBottomLeft.AddPoint_2D(*coord6)
    ringBottomLeft.AddPoint_2D(*coord3)
    polyBottomLeft = ogr.Geometry(ogr.wkbPolygon)
    polyBottomLeft.AddGeometry(ringBottomLeft)

    ringBottomRight = ogr.Geometry(ogr.wkbLinearRing)
    ringBottomRight.AddPoint_2D(*coord4)
    ringBottomRight.AddPoint_2D(*coord5)
    ringBottomRight.AddPoint_2D(*coord8)
    ringBottomRight.AddPoint_2D(*coord7)
    ringBottomRight.AddPoint_2D(*coord4)
    polyBottomRight = ogr.Geometry(ogr.wkbPolygon)
    polyBottomRight.AddGeometry(ringBottomRight)

    # Intersect 4 squares polygons with test polygon
    print polyTopLeft,geom_poly
    quaterPolyTopLeft = polyTopLeft.Intersection(geom_poly)
    quaterPolyTopRight =  polyTopRight.Intersection(geom_poly)
    quaterPolyBottomLeft =  polyBottomLeft.Intersection(geom_poly)
    quaterPolyBottomRight =  polyBottomRight.Intersection(geom_poly)

    # Create centroids of each intersected polygon
    centroidTopLeft = quaterPolyTopLeft.Centroid()
    centroidTopRight =  quaterPolyTopRight.Centroid()
    centroidBottomLeft =  quaterPolyBottomLeft.Centroid()
    centroidBottomRight =  quaterPolyBottomRight.Centroid()
    
    return centroidTopLeft,centroidTopRight,centroidBottomLeft,centroidBottomRight


def landing(stand_centroid):
    '''
    Determines closest road (landing_coord) to stand_wkt on OSM road. 
    '''

    # Create centroid of harvest area 
    centroid_geom = stand_centroid
    
    # Transform to WGS84
    sourceSR = osr.SpatialReference()
    sourceSR.ImportFromEPSG(26913)
    targetSR = osr.SpatialReference()
    targetSR.ImportFromEPSG(4326) 
    coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
    centroid_geom.Transform(coordTrans)
    centroidLon = centroid_geom.GetX()  
    centroidLat = centroid_geom.GetY()

    # get nearest point on road from centroid as json string
    headers = {'User-Agent': 'Forestry Scenario Planner'}
    url = "http://router.project-osrm.org/nearest?loc=%f,%f" % (centroidLat, centroidLon)
    tmp = tempfile.gettempdir()
    key = os.path.join(tmp, "%s_%s-None.cache" % (centroidLat, centroidLon))
    if os.path.exists(key):
        # READING FROM CACHE
        with open(key, 'r') as cache:
            data = json.loads(cache.read())
    else:
        response = requests.get(url, headers=headers)
        binary = response.content
        data = json.loads(binary)
        # WRITING TO CACHE
        with open(key, 'w') as cache:
            cache.write(json.dumps(data))

    # parse json string for landing coordinate
    landing_lat, landing_lon = data['mapped_coordinate']
    landing_geom = ogr.Geometry(ogr.wkbPoint) 
    landing_geom.AddPoint_2D(landing_lon, landing_lat)

    # Transform to local Spatial Reference
    sourceSR = osr.SpatialReference()
    sourceSR.ImportFromEPSG(4326)  # WGS84
    targetSR = osr.SpatialReference()
    targetSR.ImportFromEPSG(26913) 
    coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
    landing_geom.Transform(coordTrans)
    return landing_geom 


def skidDist(stand_wkt):
    '''
    Determines distance from any given point in stand to landing_stand_geom
    '''
    
    # Create four stand centroids
    centroids = createQuaterCentroids(stand_wkt)

    # Get four landing coordiantes
    landing_geom0 = landing(centroids[0]) 
    landing_geom1 = landing(centroids[1]) 
    landing_geom2 = landing(centroids[2]) 
    landing_geom3 = landing(centroids[3])   

    # Create a memory layer to rasterize from.
    rast_ogr_ds = ogr.GetDriverByName('Memory').CreateDataSource( 'wrk' )
    lyr = rast_ogr_ds.CreateLayer( 'poly')
    feat = ogr.Feature( lyr.GetLayerDefn() )
    feat.SetGeometryDirectly( ogr.Geometry( wkt = stand_wkt) )
    lyr.CreateFeature( feat )
    x_min, x_max, y_min, y_max = lyr.GetExtent()
  

    # Create temporary raster file and rasterize stand_wkt
    pixel_size = 10
    NoData_value = 255
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    target_ds = gdal.GetDriverByName('MEM').Create('', x_res, y_res, 1, gdal.GDT_Byte)
    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(NoData_value)
    gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])

    # Read as array
    array = band.ReadAsArray()

    # array2skidDistList
    count = 0
    standPointList = np.where(array == 1)
    skidDistList= []
    multipoint = ogr.Geometry(ogr.wkbMultiPoint)
    for indexY in standPointList[0]:
        indexX = standPointList[1][count]
        geotransform = target_ds.GetGeoTransform()
        originX = geotransform[0]
        originY = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]
        Xcoord = originX+pixelWidth*indexX
        Ycoord = originY+pixelHeight*indexY
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(Xcoord, Ycoord)
        # Get distance to four landings and take shortest
        distList = []
        distList.append(landing_geom0.Distance(point))
        distList.append(landing_geom1.Distance(point))
        distList.append(landing_geom2.Distance(point))
        distList.append(landing_geom3.Distance(point))
        skidDistList.append(min(distList))

    # Calculate final SkidDist
    SkidDist = (sum(skidDistList)/float(len(skidDistList)))*3.28084  # convert to feet

    return SkidDist




