library(leafletR)
library(sp)
library(KernSmooth)
library(RColorBrewer)
library(RJSONIO)

shakes <- fromJSON(paste(readLines("./data.json"), collapse=""))
len <- length(shakes$points)
len
coord <- data.frame(lat=numeric(),lng=numeric(),count=numeric())
for(i in 1:len){
  lng <- shakes$points[[i]]$lng
  lat <- shakes$points[[i]]$lat
  count <- shakes$points[[i]]$count
  coord <-rbind(coord, data.frame(lat=lat, lng=lng, count=count))
}
d2d = bkde2D(cbind(coord$lng,coord$lat),bandwidth=c(0.01,0.01))
#contour(d2d$x1,d2d$x2,d2d$fhat)
