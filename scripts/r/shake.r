#script to read json and write contour shpe file
shakes <- fromJSON(paste(readLines("./data.json"), collapse=""))
len <- length(shakes$points)
coord <- data.frame(lat=numeric(),lng=numeric(),count=numeric())
coord <-rbind(coord, data.frame(lat=lat, lng=lng, count=count))

for(i in 1:len){
  lng <- shakes$points[[i]]$lng
  lat <- shakes$points[[i]]$lat
  val <- shakes$points[[i]]$val
}
spatstat.options(checkpolygons = FALSE)
lngmax=max(coord$lng)
lngmin=min(coord$lng)
latmax=max(coord$lat)
latmin=min(coord$lat)
ow <- owin(c(lngmin,lngmax),c(latmin,latmax))
win =as(ow, "owin")


mx.points <- as.ppp(ppp(
  coord$lng,
  coord$lat,
  window = win  ##The extenct of the Monterrey metro area
))


mx.points

crds <- coordinates(as.points(mx.points))
poly <- crds[chull(mx.points),]

poly

mserw <- mse2d(as.points(mx.points), poly=poly, nsmse=100, range=1)
