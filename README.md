# magD
A routine for looking at magnitude detection thresholds using noise pdfs and
the Brune model, written by Dan McNamara in C and ported to python

[![PyPI version](https://badge.fury.io/py/MagD.svg)](https://badge.fury.io/py/MagD)
[![Build Status](https://travis-ci.org/travis-ci/travis-web.svg?branch=master)](https://travis-ci.org/travis-ci/travis-web)

magD has been tested on python 3.6

MagD allows an end user to evaluate seismograph performance at the network level.

## Client

An example client repo is at https://github.com/pnsn/magd_client refer to this repo for examples


## Installation
pip install magD


## Pofiles
### Magnitude thresholds
Magnitude thresholds use noise PSD's from IRIS https://service.iris.edu/mustang/noise-psd/1/

The noise at the local station is used to determine the smallest magnitude it can detect for a given origin. For each origin(lat/lon) every station in the set in analyzed, the sorted by magnitude form smallest to highest. The origin is then contoured by the nth (num_stations) smallest magnitude.

### Density
The station density is plotted for each origin and contours by distance to the nth (num_stas) closest station

### Warning Time
The map is contoured by Alert time - S wave arrival time where alert time is p-wave arrival at nth station + processing time)

### Blindzone 
The size of the EEW blindzone for a given area


