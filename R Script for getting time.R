## Get travel time by destination and different mode

install.packages("gmapsdistance")
library("gmapsdistance")

## This is my personal API
set.api.key("AIzaSyCJnz9dwMTva-N8xTMC-MQGgFQRnqK4Hh8")

results <- gmapsdistance(origin = "Washington+DC",
                         destination = "New+York+City+NY",
                         mode = "driving")

origin = c("40.431478+-80.0505401", "33.7678359+-84.4906438")
destination = c("43.0995629+-79.0437609", "41.7096483+-86.9093986")
results = gmapsdistance(origin,
                        destination,
                        mode = "bicycling",
                        shape="long")

results
