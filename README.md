# magD

A routine for looking at magnitude detection thresholds using noise pdfs and
the Brune model, written by Dan McNamara in C and ported to python

magD has been tested on python 3.5 and greater

## Client

An example client repo is at https://github.com/pnsn/magd_client refer to this repo for details


## Installation

### Basemap

Basemap is the mapping library for matplotlib. It needs to be built against geos.

### OSX

`brew install geos`

`pip3 install https://github.com/matplotlib/basemap/archive/v1.1.0.tar.gz`



### Use
To use in dev mode
pip install -e .

## Output

The MagD routine outputs objects of class MapGrid, which are saved by pickling.

The MapGrid object is then used to plot using plotMagD.py, see client, above, for details

# MapGrid object
Class details comming soon, see class if you just can't wait!
