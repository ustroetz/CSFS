from osgeo import ogr
import os
import rasterstats

def get_zonal_stats(stand_wkt):
    cur_path = os.path.dirname(os.path.realpath(__file__))
    cost_raster = cur_path + '/data/CostSurface_final.tif'
    cost = rasterstats.raster_stats(stand_wkt, cost_raster,stats=['mean'])
    return cost
