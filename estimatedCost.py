from osgeo import ogr
import rasterstats

def get_zonal_stats(stand_wkt):
    cost_raster = 'data/CostSurface.tif'
    cost = rasterstats.raster_stats(stand_wkt, cost_raster,stats=['mean'])  
    return cost
