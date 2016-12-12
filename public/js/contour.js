$(function(){  
  var layer = new L.StamenTileLayer("toner");

  var map = new L.Map("map", {
        center: [43, -120],
        zoom: 7
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
      3.0
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

	info.update = function (d) {
		this._div.innerHTML = '<h4>Lowest Min Mag Detection </h4>' +  (d ?
			'<b>' + d.properties.z + '</b><br />'
			: 'Hover over a contour');
	};

	info.addTo(map);
  
    
	function highlightFeature(d) {
    d3.select(this).style('stroke-width', 6);
    info.update(d);
	}


	function resetHighlight(d) {
    d3.select(this).style('stroke-width', 4);
    info.update();
	}
  
  d3.json("json/geomagD.json", function(data) {
    var colors = setColorScale(data);
    //2dim array=isolined.features[i].geometry.coordinates
    //level=isolined.features[i].properties.z
    var isolines = turf.isolines(data, 'z',30, mags);
    var transform = d3.geo.transform({
        point: projectPoint
    });
    var path = d3.geo.path().projection(transform);

    var contourPath = g.selectAll("path")
    .data(isolines.features)
    .enter().append("path")
    .style("fill", "none")
    
    .style("stroke", function(d,i) {return colors(d.properties.z);})
    .style('stroke-width', 3)
    .on('mouseover', highlightFeature)        
    .on('mouseout', resetHighlight);


    function reset() {
      contourPath.attr("level", function(d){
        // console.log("bing");
        return d.level;
      });
      contourPath.attr("d", function(d) {
          var pen="M";
          var pathStr = d['geometry']['coordinates'].map(function(d1) {
            // console.log(d1);
            var point = map.latLngToLayerPoint(new L.LatLng(d1[0], d1[1]));
              str=pen + point.x + "," + point.y;
              // console.log(str)
              pen= "L";
              return str;
              
          }).join('');
          return pathStr;
      });

    }

    function projectPoint(x, y) {
        var point = map.latLngToLayerPoint(new L.LatLng(y, x));
        this.stream.point(point.x, point.y);
    }
    map.on("viewreset", reset);
    reset();
    
    
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

      map.on("viewreset", update);
      update();

      function update() {
        station.attr("transform",
        function(d) {
          return "translate("+
            map.latLngToLayerPoint(d.LatLng).x +","+
            map.latLngToLayerPoint(d.LatLng).y +")";
          }
        );
      }
    });  




  });
  function setColorScale(data){
    
    return d3.scale.linear().domain([2.5,1])
        .range([d3.rgb(255,0,0), d3.rgb(0,0,255)]);
    // return d3.scale.cubehelix().domain([3,0])
    //     .range([d3.hsl(276, .6, 0), d3.hsl(96, .6, 1)]);
        // .range([d3.hsl(198, 1, .50), d3.hsl(0, 1, .50)]);
    
    // .range([d3.hsl(270, .75, .35), d3.hsl(70, 1.5, .8)]);
        // .range([d3.hsl(-40, .6, .3), d3.hsl(60, .6, 1), d3.hsl(160, .6, .3)])
        //.range([d3.hsl(-120, .6, 0), d3.hsl(60, .6, 1)]);
  }
  

  
});
