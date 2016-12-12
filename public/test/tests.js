var poly2=[[0,0],[5,0],[5,5],[0,5],[0,0]];

QUnit.test( "point in/out poly", function( assert ) {
  // console.log(poly2);
  assert.ok( pointInPoly(4,4, poly2), "Passed in poly" );
  assert.notOk( pointInPoly(6,6, poly2), "Passed not in poly" );
  assert.notOk( pointInPoly(5,5, poly2), "Passed On line test" );
  
});

QUnit.test( "poly in/out poly", function( assert ) {
  var poly1=[[1,1],[2,1],[2,2],[1,2],[1,1]];
  assert.ok( polyInPoly(poly1, poly2), "Passed in poly" );  
  assert.notOk( polyInPoly(poly2, poly1), "Passed in poly" );  
});
