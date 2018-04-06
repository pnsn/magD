#magD
A routine for looking at magnitude detection thresholds using noise pdfs and
the Brune model, written by Dan McNamara in C and ported to python

##Config
config is managed via files in config/config.ini
NSLC data come from csv/[key].csv

The runs are done using the magD script and controlled using a key that matches the keys in config/config.ini
and naming convention of csv file

Example:      

```python magD/magD.py -k  pnsn_onshore,cn_onshore,nc_onshore -o pnsn.png -p
  ..k is a comma seperated list of keys that map to the config keys, and the corresponding csv/[key].csv file
  ..p plots contours
  ..-o is output file
```



###HTTP client (needs a bit of work)
Uses Marching Squares for contouring
https://github.com/RaumZeit/MarchingSquares.js
