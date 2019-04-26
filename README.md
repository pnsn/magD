# magD

A routine for looking at magnitude detection thresholds using noise pdfs and
the Brune model, written by Dan McNamara in C and ported to python

magD has been tested on python 3.5 and greater

MagD allows an end user to evaluate seismograph performance at the network level.

## Client

An example client repo is at https://github.com/pnsn/magd_client refer to this repo for details


## Installation

### Basemap

Basemap is the mapping library for matplotlib. It needs to be built against geos.

### OSX

`brew install geos`

`brew install proj`

`pip install obspy`

`conda install -c anaconda basemap`

`conda install basemap-data-hires`
