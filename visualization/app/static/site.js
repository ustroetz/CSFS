var map = L.map('map').setView([40.545, -105.965], 14);

baseLayers = {
  "Satellite" : L.mapbox.tileLayer('tmcw.map-j5fsp01s'),
  "Terrain" :  L.mapbox.tileLayer('tmcw.map-7s15q36b').addTo(map),
};

overlays = {
  'Cost Surface': L.mapbox.tileLayer('ustroetz.t').addTo(map),
};

// Add a layer control element to the map
layerControl = L.control.layers(baseLayers, overlays, {position: 'topleft'});
layerControl.addTo(map);

var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
  draw: {polyline: false,
	  rectangle:false,
	  circle:false,
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
}).addTo(map);


	
map.on('draw:edited', function (e) {
	drawnItems.eachLayer(function (layer){
		getEstimate(layer);
	});

	if ($('#spatial_var tbody').children().length != 0 ){
		$('#spatial_var').empty();
		$("#calculate").css("display", "block");
		$("#recalculate").css("display", "none");

	};
});

map.on('draw:drawstart', function (e){
	$("#infoStart").remove();
	$("#estimated_cost").empty();
	drawnItems.eachLayer(function (layer){
		map.removeLayer(layer)
	});

	if ($('#spatial_var tbody').children().length != 0 ){
		$('#spatial_var').empty();
		$("#calculate").css("display", "block");
		$("#recalculate").css("display", "none");

	};
	});

map.on('draw:created', function (e) {
	getEstimate(e.layer)
});


var getEstimate = function (layer) {
	var geojson = layer.toGeoJSON();
    var wkt = Terraformer.WKT.convert(geojson.geometry);
	
	drawnItems.addLayer(layer);
	document.getElementById('estimated_cost').innerHTML = 'No Data';

      $(function() {
        $(function() {
          $.getJSON('/_send_wkt', {data: wkt,}, 		
  		function(data) {
            $(data.result);	
            var cost = data.result + ' $/ton';
            document.getElementById('text_estimated_cost').innerHTML = 'Harvest Cost Estimate';
			document.getElementById('estimated_cost').innerHTML = cost;	


			document.getElementById('estimate').style.visibility = 'visible';
          });
        });
    });
 };



function calculate(){

		  // Get Input Variables		  
		  var TPA = document.getElementById('TPA').value;
		  if(! TPA){
		    TPA = 300
		  }
		  else {
		  	 TPA = parseFloat(TPA);
		  };
		  
		  var VPA = document.getElementById('VPA').value;
		  if(! VPA){
		    VPA = 4000
		  }
		  else {
		  	 VPA = parseFloat(VPA);
		  };

		  var SD = document.getElementById('SD');
		  if(! SD){
		    SD = null
		  }
		  else {
		  	 SD = parseFloat(SD.value);
		  };

		  var S = document.getElementById('S');
		  if(! S){
		    S = null
		  }
		  else {
		  	 S = parseFloat(S.value);
		  };

		var wkt;
		if ((drawnItems.getLayers().length) != 0){
		drawnItems.eachLayer(function(layer){
			wkt = Terraformer.WKT.convert((layer.toGeoJSON()).geometry);
			});

		  var harvest_data = {TPA: TPA, VPA: VPA, SD: SD, S: S, stand_wkt: wkt};
		  var harvest_data_str = JSON.stringify(harvest_data);

	      $(function() {
	        $(function() {
	          $.getJSON('/_send_TreeData', {harvest_data: harvest_data_str,}, 
			  		
	  		function(data) {
	            $(data.result);	
	   			 var table_spatial_var = document.getElementById('spatial_var');

	   			 if ($('#spatial_var tbody').children().length == 0 ){
		   			 // Skidding Distance
		             var row = table_spatial_var.insertRow(0);
		             var cellSD = row.insertCell(0);
					 var cellSDvalue = row.insertCell(1);
					 var SDvalue = String(parseFloat(data.result[1]));
					 cellSD.innerHTML = "Skidding Distance";
					 cellSDvalue.innerHTML = "<input type='range' min='0' max='10000' step='100' value='" + SDvalue + "' onchange='SD.value=value'></input><output id='SD'>" + SDvalue + "</output><output> ft</output></td>";
					 // Slope
					 var row = table_spatial_var.insertRow(1);
		             var cellS = row.insertCell(0);
					 var cellSvalue = row.insertCell(1);
					 var Svalue = String(parseFloat(data.result[0]));
					 cellS.style.width = "143px";
					 cellS.innerHTML = "Slope";
					 cellSvalue.innerHTML = "<input type='range' min='0' max='40' step='1' value='" + Svalue + "' onchange='S.value=value'></input><output id='S'>" + Svalue + "</output><output> %</output></td>";
					 // Cost
					 var row = table_spatial_var.insertRow(2);
					 var cell1 = row.insertCell(0);
					 cell1.innerHTML = "&nbsp;"
					 var row = table_spatial_var.insertRow(3);
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
				 	table_spatial_var.rows[3].cells[1].innerHTML = String(parseFloat(data.result[2])) + " $/ton";
				 };
				 
				 
				 });
	        });
	      });}
	      else {alert('Please digitize a stand first!')};
};
$('#expander').simpleexpand();
