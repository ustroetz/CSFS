// Create map elements
var map = L.map('map').setView([40.545, -105.965], 14);

var csf = L.geoJson(csf, {
    style: {
        opacity: 1.0,
        fill: 0.0,
        color: '#FFF'
    }
});
var satelliteTileLayer = L.tileLayer('https://{s}.tiles.mapbox.com/v3/tmcw.map-j5fsp01s/{z}/{x}/{y}.png');
var terrainTileLayer = L.tileLayer('https://{s}.tiles.mapbox.com/v3/tmcw.map-7s15q36b/{z}/{x}/{y}.png');
var costSurfaceTileLayer = L.tileLayer('https://{s}.tiles.mapbox.com/v3/csfsfc.t/{z}/{x}/{y}.png', {
    opacity: 0.5
    });

baseLayers = {
    "Satellite": satelliteTileLayer,
    "Terrain": terrainTileLayer
};

overlays = {
    'Cost Surface': costSurfaceTileLayer,
};

var layerControl = L.control.layers(baseLayers, overlays, {
    position: 'topleft'
});

var drawnItems = new L.FeatureGroup();

var drawControl = new L.Control.Draw({
    draw: {
        polyline: false,
        rectangle: false,
        circle: false,
        marker: false,
        polygon: {
            shapeOptions: {
                color: '#80c757'
            }
        }
    },
    edit: {
        featureGroup: drawnItems
    }
});


terrainTileLayer.addTo(map);
csf.addTo(map);
layerControl.addTo(map);
drawControl.addTo(map);
drawnItems.addTo(map)


// Create event listener	
map.on('draw:edited', function(e) {
    // after stand is edited: recalcualte estimate, remove detailed calculation

    drawnItems.eachLayer(function(layer) {
        getEstimate(layer);
    });

    if ($('#spatial_var tbody').children().length != 0) {
        $('#spatial_var').empty();
        $("#calculate").css("display", "block");
        $("#recalculate").css("display", "none");
    };
});

map.on('draw:drawstart', function(e) {
    // after stand drawing started: remove info start box, empty cost estimate, remove previous stand layers, remove detailed caluclation

    $("#infoSign").remove();

    $("#estimated_cost").empty();
    drawnItems.eachLayer(function(layer) {
        map.removeLayer(layer)
    });

    if ($('#spatial_var tbody').children().length != 0) {
        $('#spatial_var').empty();
        $("#calculate").css("display", "block");
        $("#recalculate").css("display", "none");
    };
});

map.on('draw:created', function(e) {
    // after stand is drawn: calculate estimate

    getEstimate(e.layer)
});


var getEstimate = function(layer) {

    // add layer to map and add 'No Data' defautl to info box
    drawnItems.addLayer(layer);
    document.getElementById('estimated_cost').innerHTML = 'No Data';

    // convert layer to wkt
    var standGeojson = layer.toGeoJSON();
    var standWKT = Terraformer.WKT.convert(standGeojson.geometry);

    // send wkt to Python App to get cost estimate
    $(function() {
        $.getJSON('/_estimatedCost', {
                data: standWKT
            },
            function(data) {
                $(data.result);

                // Update cost estimate in info box
                var cost = data.result + ' $/ton';
                document.getElementById('text_estimated_cost').innerHTML = 'Harvest Cost Estimate';
                document.getElementById('estimated_cost').innerHTML = cost;
                document.getElementById('estimate').style.visibility = 'visible';
            });
    });
};



var calculate = function() {

    // Get Input Variables		  
    var TPA = document.getElementById('TPA').value;
    if (!TPA) {
        TPA = 300
    } else {
        TPA = parseFloat(TPA);
    };

    var VPA = document.getElementById('VPA').value;
    if (!VPA) {
        VPA = 4000
    } else {
        VPA = parseFloat(VPA);
    };

    var SD = document.getElementById('SD');
    if (!SD) {
        SD = null
    } else {
        SD = parseFloat(SD.value);
    };

    var S = document.getElementById('S');
    if (!S) {
        S = null
    } else {
        S = parseFloat(S.value);
    };

    // get stand layer
    var standWKT;
    if ((drawnItems.getLayers().length) != 0) {
        drawnItems.eachLayer(function(layer) {
            standWKT = Terraformer.WKT.convert((layer.toGeoJSON()).geometry);
        });

        var harvestData = {
            TPA: TPA,
            VPA: VPA,
            SD: SD,
            S: S,
            stand_wkt: standWKT
        };
        var harvestDataStr = JSON.stringify(harvestData);

        // send harvest data string to Python App to get cost calculation
        $(function() {
            $.getJSON('/_calculatedCost', {
                    harvest_Data: harvestDataStr
                },

                function(data) {
                    $(data.result);

                    // Update spatial variables and detailed cost
                    var tableSpatialData = document.getElementById('spatial_var');

                    if ($('#spatial_var tbody').children().length == 0) {
                        // Skidding Distance
                        var row = tableSpatialData.insertRow(0);
                        var cellSD = row.insertCell(0);
                        var cellSDvalue = row.insertCell(1);
                        var SDvalue = String(parseFloat(data.result[1]));
                        cellSD.innerHTML = "Skidding Distance";
                        cellSDvalue.innerHTML = "<input type='range' min='0' max='10000' step='100' value='" + SDvalue + "' onchange='SD.value=value'></input><output id='SD'>" + SDvalue + "</output><output> ft</output></td>";
                        // Slope
                        var row = tableSpatialData.insertRow(1);
                        var cellS = row.insertCell(0);
                        var cellSvalue = row.insertCell(1);
                        var Svalue = String(parseFloat(data.result[0]));
                        cellS.style.width = "143px";
                        cellS.innerHTML = "Slope";
                        cellSvalue.innerHTML = "<input type='range' min='0' max='40' step='1' value='" + Svalue + "' onchange='S.value=value'></input><output id='S'>" + Svalue + "</output><output> %</output></td>";
                        // Cost
                        var row = tableSpatialData.insertRow(2);
                        var cell1 = row.insertCell(0);
                        cell1.innerHTML = "&nbsp;"
                        var row = tableSpatialData.insertRow(3);
                        var cellC = row.insertCell(0);
                        var cellCvalue = row.insertCell(1);
                        cellCvalue.innerHTML = String(parseFloat(data.result[2])) + " $/ton";
                        cellC.innerHTML = "Cost";
                        // Buttons
                        document.getElementById("calculate").style.display = "none";
                        document.getElementById("recalculate").style.display = "block";
                    }

                    // Recalculate
                    else {
                        document.getElementById("SD").value = parseFloat(data.result[1]);
                        document.getElementById("S").value = parseFloat(data.result[0]);
                        tableSpatialData.rows[3].cells[1].innerHTML = String(parseFloat(data.result[2])) + " $/ton";
                    };
                });
        });
    } else {
        alert('Please digitize a stand first!')
    };
};

// Expand info box
$('#expander').simpleexpand();
