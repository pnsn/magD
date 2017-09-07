$(function(){  
  var layer = new L.StamenTileLayer("toner");
  
  
  
  
  $.urlParam = function(name){
      var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
      if (results==null){
         return null;
      }
      else{
         return results[1] || 0;
      }
  };
  var latCenter=$.urlParam('latCenter');
  var lonCenter=$.urlParam('lonCenter');
  var dataFile=$.urlParam('dataFile');
  var mapZoom=$.urlParam('mapZoom');
  // alert(latCenter);
  // var lonCenter=$.url().param('lonCenter');
  // var dataFile=$.url().param('dataFile');
  
  
  
  var map = new L.Map("map", {
        center: [latCenter, lonCenter],
        zoom: mapZoom
      }).addLayer(layer);
  map._initPathRoot();
  //debugging. Only show these mags. If empty, no debugging
  var filterVals=[]; 
  var filterOutVals=[];
  // var mags= [-0.5, 0,  0.5,  1.0,  1.5, 2.0, 2.5, 3.0];
  // var mags= [-0.5, -0.75, 0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0 ];
  // var mags =[-1.0, -0.125, -0.25, -0.375, -0.5, -0.625, -0.75, -0.875,
  //     0.0 ,0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875,
  //     1.125, 1.25, 1.375, 1.5, 1.625, 1.75, 1.875,
  //     2.125, 2.25, 2.375, 2.5, 2.625, 2.75, 2.875, 3.0];
  var mags = [
      0.0 ,0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
      1.0 ,1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9,
      2.0 ,2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9,
      3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 
      4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9
  ];
  // mags=[1.3, 1.4];
  
  var svg = d3.select("#map").select("svg");
  var g = svg.append("g").attr("class", "leaflet-zoom-hide").attr('opacity', .75);

	// control that shows state info on hover
	var info = L.control();

	info.onAdd = function (map) {
		this._div = L.DomUtil.create('div', 'info');
		this.update();
		return this._div;
	};

	info.update = function (c) {
		this._div.innerHTML = '<h4>Lowest Min Mag Detection </h4>' +  (c ?
			'<b>' + c.level + '</b><br />'
			: 'Hover over a contour');
	};

	info.addTo(map);
  
    
	function highlightFeature(d) {
    d3.select(this).style('stroke', 'black');
    d3.select(this).style('opacity', 0.9);

    // if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
    //   layer.bringToFront();
    // }

    info.update(d);
	}


	function resetHighlight(d) {
    d3.select(this).style('stroke', 'white');
    d3.select(this).style('opacity', 1);
    info.update();
	}
  
  d3.json("json/"+ dataFile + ".json", function(data) {
  
    var colors = setColorScale(data); 
    var bands = bandGridData(data, mags);
    bands= sortContours(bands);
    
    
    if(filterVals.length >0){
      bands = filterBands(bands, filterVals);
    }
    if(filterOutVals.length >0){
      bands=filterOutBands(bands, filterOutVals);
    }
    
      
    
      
    var transform = d3.geo.transform({
        point: projectPoint
    });
    var path = d3.geo.path().projection(transform);

    var contourPath = g.selectAll("path")
    .data(bands)
    .enter().append("path")
    .style("fill", function(d, i) { return colors(d.level);})
    .style("stroke", "white")
    .style('stroke-width', 1)
    .style('opacity', 1)
    .on('mouseover', highlightFeature)        
    .on('mouseout', resetHighlight);
  
    function resetContours() {
      contourPath.attr("level", function(d){
        return d.level;
      });
    
      contourPath.attr("d", function(d) {
          var pathStr = d.map(function(d1) {
            var point = map.latLngToLayerPoint(new L.LatLng(d1[1], d1[2]));
              return d1[0] + point.x + "," + point.y;
              // return d1[0] + d1[1] + "," + d1[2];
          }).join('');
          return pathStr;
      });                          

    }
    
    function projectPoint(x, y) {
        var point = map.latLngToLayerPoint(new L.LatLng(y, x));
        this.stream.point(point.x, point.y);
    } 
    map.on("viewreset", resetContours);
    resetContours();  
    
    
    d3.json("json/scnls.json", function(collection) {
      /* Add a LatLng object to each item in the dataset */
      collection.scnls.forEach(function(d) {
        d.LatLng = new L.LatLng(d.lat,
            d.lon);
      });


        var station = g.selectAll(".mark")
            .data(collection.scnls)
            .enter()
            .append("image")
            .attr('class','mark')
            .attr('width', 10)
            .attr('height', 10)
            .attr("xlink:href",'images/triangle-red.png')
            .attr("opacity", 0.8);

      map.on("viewreset", resetStations);
      resetStations();

      function resetStations() {
        
        station.attr("transform",
        function(d) {
          return "translate("+
            map.latLngToLayerPoint(d.LatLng).x +","+
            map.latLngToLayerPoint(d.LatLng).y +")";
          }
        );
        
        station.attr("d", function(d){
          $("#station-info table tbody").append("<tr><td>" +d.sta +"</td><td>" +d.chan +"</td></tr>");
        });
        
        
        
        
      }
    
    });  

  });
  function setColorScale(data){
    return d3.scale.cubehelix().domain([data.max,data.min])
    // .range([d3.hsl(198, 1, .50), d3.hsl(0, 1, .50)]);
    
        .range([d3.hsl(276, .6, 0), d3.hsl(96, .6, 1)]);
    
    // .range([d3.hsl(270, .75, .35), d3.hsl(70, 1.5, .8)]);
        // .range([d3.hsl(-40, .6, .3), d3.hsl(60, .6, 1), d3.hsl(160, .6, .3)])
        //.range([d3.hsl(-120, .6, 0), d3.hsl(60, .6, 1)]);
  }
  

  
});
