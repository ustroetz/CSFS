from flask import Flask, render_template, request, jsonify
import zonal_stats as stats
import harvest_cost as hs
import json

app = Flask(__name__)
app.config['DEBUG'] = True



@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")
    
    
@app.route('/_send_wkt')
def get_cost_estimate():
    stand_wkt = request.args.get('data')
    cost_stats = stats.get_zonal_stats(stand_wkt)
    cost = round(cost_stats[0]['mean'],2)
    return jsonify(result = cost)
    

@app.route('/_send_TreeData')
def get_cost_detailed():
    harvestData = json.loads(request.args.get('harvest_data'))
    slope, SkidDist, harvestCostTon,totalHarvestCost = hs.cost_func(str(harvestData['stand_wkt']), harvestData['TPA'], harvestData['VPA'], harvestData['SD'], harvestData['S'])    
    totalHarvestCost = round(totalHarvestCost,2)
    harvestCostTon = round(harvestCostTon,2)
    SkidDist = round(SkidDist,2)
    slope = round(slope,2)
    print slope
    resultData = [slope, SkidDist, harvestCostTon, totalHarvestCost]
    print resultData
    
    return jsonify(result = resultData)
    

if __name__ == "__main__":
    app.run()