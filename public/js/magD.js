$(function(){  
  var layer = new L.StamenTileLayer("toner");

  var map = new L.Map("map", {
        center: [43, -120],
        zoom: 7
      })
      .addLayer(layer);
  map._initPathRoot();


  var svg = d3.select("#map").select("svg");
  var g = svg.append("g").attr("class", "leaflet-zoom-hide").attr('opacity', 0.8);

  var defaultContourColor = 'white';
  var defaultContourWidth = 1;

  // var colors = d3.scale.cubehelix().domain([0,4]);
  // var colors = d3.scale.linear().domain([-1,1,3]).range(['#ffeda0',"#feb24c",'#f03b20']);
  var colors = d3.scale.linear().domain([-1,3]).range(['green', 'red']);

  bands=[];
  d3.json("json/magDgrid.json", function(data) {
    var l=-5;
    var mags= [-0.5, -0.75, 0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0 ];
    // var mags= [-0.5, 0,  0.5,  1.0,  1.5, 2.0, 2.5, 3.0];
  
    for(var i=0; i< mags.length-1; i++){
      var isoband=MarchingSquaresJS.IsoBands(data.grid,mags[i], mags[i+1]);
      for(var j=0;j<isoband.length;j++){
        var band=[];
        var pen = "M";
        for(var k=0;k<isoband[j].length; k++){
          // console.log(Math.round(isoband[j][k][0])+ ": " + Math.round(isoband[j][k][1]));
          var lat=data.lat_start + isoband[j][k][1]*data.lat_step;
          var lon=isoband[j][k][0]*data.lon_step + data.lon_start;
          band.push([pen,lat,lon]);
          pen = "L";
        }
        if( band !==undefined && band.length> 1){
          band.level=mags[i];
          bands.push(band);
        }
      
      }
    }

    // bands.sort(function(a,b) {
    //     return b.level - a.level;
    // });
  
  
      
  
    var transform = d3.geo.transform({
        point: projectPoint
    });
    var path = d3.geo.path().projection(transform);

  
    var contourPath = g.selectAll("path")
    .data(bands)
    .enter().append("path")
    .style("fill", function(d, i) { return colors(d.level);})
    .style("stroke", defaultContourColor)
    .style('stroke-width', defaultContourWidth)
    .style('opacity', .6)
    .on('mouseover', function(d) {
        d3.select(this).style('stroke', 'black');
        // d3.select(this).style('opacity',.9);
        console.log(d3.select(this).attr('level'));
    })
    .on('mouseout', function(d) {
        d3.select(this).style('stroke', defaultContourColor);
        d3.select(this).style('opacity', .6);
      
    });
    // drawLegend();
  
    function reset() {
      contourPath.attr("level", function(d){
        return d.level;
      });
    
        contourPath.attr("d", function(d) {
            var pathStr = d.map(function(d1) {
              var point = map.latLngToLayerPoint(new L.LatLng(d1[1], d1[2]));
                return d1[0] + point.x + "," + point.y;
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
    
    

  });
});