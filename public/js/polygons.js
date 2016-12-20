//Does poly 1 fit inside poly2?
//consider each point in poly1 and check if it is 
function polyInPoly(poly1, poly2){
  for(var i=0; i< poly1.length; i++){    
    if(!pointInPoly(poly1[i][1], poly1[i][2], poly2)){
      return false;
    }
  }
  return true;
}


function pointInPoly(x,y, poly2){
 // ray-casting algorithm based on
  // http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
  var inside = false;
  for (var i = 0, j = poly2.length - 1; i < poly2.length; j = i++) {
      var xi = poly2[i][1], yi = poly2[i][2];
      var xj = poly2[j][1], yj = poly2[j][2];

      var intersect = ((yi > y) != (yj > y))
          && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
      if (intersect) inside = !inside;
  }
  return inside;
  
}


// function contourGridData(data, mags){
//   var grid = setHighBoundaries(data, mags[i]);
//   // var grid = data.grid;
//   var bands=[];
//   for(var i=0; i< mags.length-1; i++){
//     if (mags[i] < data.max){
//       var contour=MarchingSquaresJS.IsoContours(grid,mags[i], mags[i+1]);
//       for(var j=0;j<contour.length;j++){
//         var band=[];
//         var pen = "M";
//         for(var k=0;k<contour[j].length; k++){
//           var lat=data.lat_start + contour[j][k][1]*data.lat_step;
//           var lon=contour[j][k][0]*data.lon_step + data.lon_start;
//           band.push([pen,lat,lon]);
//           pen = "L";
//         }
//         if( band !==undefined && band.length> 1){
//           band.level=mags[i];
//           bands.push(band);
//        }
//
//       }
//     }
//   }
//   return bands;
// }
  
  
  
  
  function bandGridData(data, mags){
    var grid = data.grid;
    
    // var grid = setHighBoundaries(data, mags[i]);
    // for(var i=0; i<grid.length; i++){
    //   var str="[";
    //   for(var j=0; j< grid[i].length; j++){
    //     var val=parseFloat((grid[i][j]).toFixed(1),0);
    //     str+="," + val;
    //   }
    //   console.log(str + "]");
    // }
    var bands=[];
    for(var i=0; i< mags.length-1; i++){
      if (mags[i] < data.max){
        var grid = setHighBoundaries(data, mags[i]);
        
        var isoband=MarchingSquaresJS.IsoBands(grid,mags[i], mags[i+1]);
        for(var j=0;j<isoband.length;j++){
          var band=[];
          var pen = "M";
          for(var k=0;k<isoband[j].length; k++){
            var lat=data.lat_start + isoband[j][k][1]*data.lat_step;
            var lon=isoband[j][k][0]*data.lon_step + data.lon_start;
            band.push([pen,lat,lon]);
            // band.push([pen, isoband[j][k][1], isoband[j][k][0]])
            pen = "L";
          }
          if( band !==undefined && band.length> 1){
            band.level=mags[i];
            bands.push(band);
         }
      
        }
      }
    }
    return bands;
  }
    //we don't want larger polyies covering smaller. Polyies are sorted small mag to big
    // so we need to ensure smalls aren't getting covered by bigs. 
    //start from back of array and move all polygons that fit into larger one back
    // until they can't fit, then insert
  function sortContours(bands){
    for(var i= bands.length -1; i > 0; i--){
      for(var j=i-1; j > 0; j--){
        
        if(polyInPoly(bands[j], bands[i])){
          var moveIndex=i;
          var moveVal=bands[j];
          //work back up the index and stop when it 
          //doesn't fit
          for(var k=i+1; k< bands.length; k++){
            if(polyInPoly(bands[j], bands[k])){
              moveIndex++;
            }
          }
          //move all inbetween contours
          for(var k=j; k < moveIndex; k++){
            bands[k]=bands[k+1];
          }
          bands[moveIndex]=moveVal;
          
        }
      } 
    }
    return bands;
    
    
  }
  
    //This isn't used. 
    //remove polyies that are of same level and fit into
    // each other. This probably could be done in sortContours but
    // since each relationship needs to be checked and poly removed 
    // from set, is cleaner to do in two steps.
  function removeSiblinginPoly(bands){
    bands=sortContoursBySize(bands);
    for(var i=0; i< bands.length ; i++){
      currentLevel=bands[i].level;
      for(var j=i; j < bands.length; j++){
        console.log(currentLevel, bands[j].level);

        if(bands[j].level==currentLevel && polyInPoly(bands[i], bands[j])){
          bands.splice(j,1);
        }
      }
    }
    return bands;
    
  }
  
//bands are already sorted by level now sort by size
  function sortContoursBySize(bands){
    bands.sort(function(a,b){
      return a.level===b.level ? a.length - b.length :0;
    });
    return bands;
  }

  
  //debugging method for filtering on mags
  function filterBands(bands, filterVals){
    var filtered = [];
    for(var i=0; i< bands.length; i++){
      for(var j=0; j< filterVals.length; j++){
        if(filterVals[j]===bands[i].level)
          filtered.push(bands[i]);
      }
      
    }
    return filtered;
  }
  //debugging method for filtering out mags
  function filterOutBands(bands, filterVals){
    for(var i=0; i< bands.length; i++){
      for(var j=0; j< filterVals.length; j++){
        if(filterVals[j]===bands[i].level)
          bands.splice(i,1);
      }
      
    }
    return bands;
  }
  
  
  //set artifically high boundaries around grid so contours will stay
  //inside polygon and not reverese the polygon.
  function setHighBoundaries(data,level){
    var grid=data.grid;
    for(var i=0; i< grid.length; i++){
      for(var j=0; j< grid[i].length; j++){
        if(i===0 || i===grid.length -1 || j===0 || j=== grid[i].length -1)
          grid[i][j]=100;
      }
    }
    return grid;
  }