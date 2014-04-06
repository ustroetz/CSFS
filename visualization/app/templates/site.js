
$('#expander').simpleexpand();



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




var drawControl = new L.Control.Draw({

  draw: {polyline: false,
	  rectangle:false,
	  circle:false,
	  marker: false,
  	},
}).addTo(map);


var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

map.on('draw:drawstart', function (e){
	var element = document.getElementById('infoStart');
	if (element != null) {
    	element.parentNode.removeChild(element);
	}});

map.on('draw:created', function (e) {
    var geojson = e.layer.toGeoJSON();
    var wkt = Terraformer.WKT.convert(geojson.geometry);
	
	drawnItems.addLayer(e.layer);
	document.getElementById('estimated_cost').innerHTML = 'No Data';

      $(function() {
        $(function() {
          $.getJSON('/_send_wkt', {data: wkt,}, 		
  		function(data) {
            $(data.result);	
            var cost = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp' + data.result + ' $/ton'
            document.getElementById('text_estimated_cost').innerHTML = 'Harvest Cost Estimate'
			document.getElementById('estimated_cost').innerHTML = cost;	


			document.getElementById('estimate').style.visibility = 'visible';
          });
        });
	  });
});


function calculate(){
		  
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

		var wkt;
		if ((drawnItems.getLayers().length) != 0){
		drawnItems.eachLayer(function(layer){

			wkt = Terraformer.WKT.convert((layer.toGeoJSON()).geometry);
			});


		  var harvest_data = {TPA: TPA, VPA: VPA, stand_wkt: wkt};
		  var harvest_data_str = JSON.stringify(harvest_data);
		  console.log(harvest_data_str);

	      $(function() {
	        $(function() {
	          $.getJSON('/_send_TreeData', {harvest_data: harvest_data_str,}, 
			  		
	  		function(data) {
	            $(data.result);	
	            console.log(data.result);
	   //          var table_spatial_var = document.getElementById('spatiaL_var');
	   //          console.log(table_spatial_var);
	   //          var row = table_spatial_var.insertRow(0);
	   //          var cell1 = row.insertCell(0);
				// var cell2 = row.insertCell(1);
				// cell1.innerHTML = "Skidding Distance";
				// cell2.innerHTML = parseFloat(data.result[1].join('.'));
	            // = parseFloat(data.result[0].join('.'));	
	            // document.getElementById('SD').value = parseFloat(data.result[1].join('.'));
	            // document.getElementById('calculated_cost').innerHTML = parseFloat(data.result[2].join('.'));	
	          });
	        });
	      });}
	      else {alert('Please digitize a stand first!')};
};