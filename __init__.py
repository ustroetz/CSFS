from flask import Flask, render_template, request, jsonify
import estimatedCost as eCost
import calculatedCost as cCost
import json

app = Flask(__name__)
app.config['DEBUG'] = True



@app.route('/')

@app.route('/index')
def index():
    return render_template("index.html")
    
    
@app.route('/_estimatedCost')
def get_cost_estimate():
    standWKT = request.args.get('data')
    costStats = eCost.get_zonal_stats(standWKT)
    cost = round(costStats[0]['mean'],2)
    return jsonify(result = cost)
    

@app.route('/_calculatedCost')
def get_cost_detailed():
    harvestData = json.loads(request.args.get('harvest_Data'))
    slope, SkidDist, harvestCostTon,totalHarvestCost = cCost.cost_func(str(harvestData['stand_wkt']), harvestData['TPA'], harvestData['VPA'], harvestData['SD'], harvestData['S'])    
    totalHarvestCost = round(totalHarvestCost,2)
    harvestCostTon = round(harvestCostTon,2)
    SkidDist = round(SkidDist,2)
    slope = round(slope,2)
    resultData = [slope, SkidDist, harvestCostTon, totalHarvestCost]    
    return jsonify(result = resultData)
    

if __name__ == "__main__":
    app.run()