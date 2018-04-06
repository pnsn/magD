#!/bin/bash
#uses plotly
docker run -it --rm -v "$PWD":/app -v /Users/joncon/.plotly:/root/.plotly joncon/mag10-3.5:latest /bin/bash
