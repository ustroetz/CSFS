from osgeo import ogr, osr
import math
from forestcost import skidding, harvesting
import rasterstats


def cost_func(stand_wkt, TPA, VPA, SkidDist, Slope):

    ### Input Data
    slope_raster = 'data/Slope.tif'
    
    # Reproject
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)

    target = osr.SpatialReference()
    target.ImportFromEPSG(  )

    transform = osr.CoordinateTransformation(source, target)

    stand_geom = ogr.CreateGeometryFromWkt(stand_wkt)
    stand_geom.Transform(transform)
    stand_wkt = stand_geom.ExportToWkt()

    ### Calculation
    area = stand_geom.GetArea()                                         # get area in m2
    area = round(area*0.000247105, 4)                                   # convert to acre and round
    if Slope == None:
        Slope = rasterstats.raster_stats(stand_wkt, slope_raster,stats=['mean'])  
        Slope = Slope[0]['mean']                                        # %

    if SkidDist == None:
        SkidDist = skidding.skidDist(stand_wkt)                         # ft

    totalVolume = area*VPA                                              # ft3
    totalWeight = totalVolume*0.0195                                    # US short tons (lodepole pine weight)
    
    harvestCostFt3 = harvesting.harvestcost(Slope, SkidDist, TPA, VPA)  # $/ft3
    totalHarvestCost = round(harvestCostFt3*totalVolume)                # $
    harvestCostTon = totalHarvestCost/totalWeight                       # $/ton
        

    return Slope, SkidDist, harvestCostTon, totalHarvestCost


