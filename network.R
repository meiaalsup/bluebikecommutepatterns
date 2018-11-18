library(igraph)
library(sna)
library(Matrix)
library(plyr)
library(qgraph)
library(data.table)
library(dplyr)
library(tidyr)
library(tidytext)
library(SparseM)
library(fansi)
library(GGally)
library(tcltk)
library(scales)


########## 0. Load in data and process ##########
# the funciton
loadData <- function(morOrEven){
  data <- read.csv(paste0("cleaneddata/Month0-cleaned-",morOrEven,".csv"), header = TRUE)
  
  for (i in 1:12){
    data_concat <- read.csv(paste0("cleaneddata/Month",i,"-cleaned-",morOrEven,".csv"), header = TRUE)
    data <- rbind(data, data_concat)
  }
  
  return(data)
}

# morning data
morning <- loadData("morning")
morning$starttime <- as.POSIXct(morning$starttime,tz=Sys.timezone())
morning$stoptime <- as.POSIXct(morning$stoptime,tz=Sys.timezone())

# evening data
evening <- loadData("evening")
evening$starttime <- as.POSIXct(evening$starttime,tz=Sys.timezone())
evening$stoptime <- as.POSIXct(evening$stoptime,tz=Sys.timezone())

# lat lon of stations
coord <- read.csv("station id.csv", header = TRUE)
rownames(coord) <- coord$start.station.id
coord$start.station.id <- NULL
coord$start.station.name <- NULL
coord <- as.matrix(coord)



########## 1. Create network of all bike stations ##########
# Create a sparse matrix that stores number of trips from which station to which station 
# in certain times
createMatrix <- function(startFromMonth, startToMonth, morOrEvenData){
  # sort data and create the pivot table matrix
  data <- morOrEvenData[(morOrEvenData$starttime >= startFromMonth) & 
                          (morOrEvenData$starttime <= startToMonth),]
  data <- data[(data$start.station.id != 164)&(data$end.station.id != 164),]
  network <- as.data.frame(spread(count(data, start.station.id, end.station.id),
                                  end.station.id, n, fill = 0))
  rownames(network) <- network$start.station.id
  network$start.station.id <- NULL
  # counting <- as.data.frame(count(morOrEvenData, start.station.id, end.station.id))
  # top <- counting[order(counting$n, decreasing = TRUE)[1:top],]
  # top <- spread(top, end.station.id, n, fill = 0)
  # rownames(top) <- top$start.station.id
  # top$start.station.id <- NULL
  # m1 <- as.matrix(top)
  m1 <- as.matrix(network)
  
  # create adjacency matrix
  union.id <- union(rownames(network), colnames(network))
  m2 <- matrix(0, length(union.id), length(union.id), dimnames = list(union.id, union.id))
  m2[row.names(m1), colnames(m1)] <- m1
  
  final.matrix <- Matrix(m2, sparse = TRUE)
  
  return(final.matrix)
}


# create 1 year data matrix
matrix.year.morning <- createMatrix("2017-10-01","2018-10-01",morning)
matrix.year.evening <- createMatrix("2017-10-01","2018-10-01",evening)


########## 2. Degree ##########
drawDegree <- function(matrix, top, morOrEven){
  graph <- graph_from_adjacency_matrix(matrix, mode = "directed", weighted = TRUE)
  degree <- igraph::strength(graph, mode = "all")
  
  # set edge color and width
  E(graph)[E(graph)$weight < sort(E(graph)$weight, decreasing = TRUE)[top]]$color <- "gray95"
  E(graph)[E(graph)$weight >= sort(E(graph)$weight, decreasing = TRUE)[top]]$color <- "orange"
  E(graph)[E(graph)$weight < sort(E(graph)$weight, decreasing = TRUE)[top]]$weight <- .1
  
  # set node color and width
  degree.df <- as.data.frame(degree)
  degree.df$color <- "gray40"
  degree.df[rownames(sort(degree.df,decreasing = TRUE))[1:top],2] <- "gold"

  # print(degree.df)

  plot.igraph(graph, 
       layout = coord[V(graph)$name,],
       vertex.size = rescale(degree, to = c(1, 10)),
       vertex.lable.dist = 1,
       vertex.label.cex = rescale(degree, to = c(.01, 2)),
       vertex.label.family = "mono",
       vertex.color = degree.df$color,
       edge.arrow.size = .1,
       edge.curved = 0,
       edge.color = E(graph)$color,
       edge.width=rescale(E(graph)$weight, to=c(0.1,20)),
       main = paste0("Degree of Bluebike stations 2017-2018 ", morOrEven," with top 50 popular routes highlighted"))
  
}

drawDegree(createMatrix("2017-10-01","2018-10-01",morning),50, "morning")



########## 3. Connected components ##########

# largest connected component
# connection <- igraph::components(graph_from_adjacency_matrix(createMatrix("2017-10-01","2017-10-10",morning),10, mode = "directed", weighted = TRUE)) 

########## 4. Communities ##########

# community based on fast greedy
# transformed to undirected graph
cfg <- cluster_fast_greedy(as.undirected(graph_from_adjacency_matrix(createMatrix("2017-10-01","2018-10-01",morning),50, mode = "directed", weighted = TRUE)))

dendPlot(cfg, mode="hclust")

plot(cfg, 
     as.undirected(graph_from_adjacency_matrix(createMatrix("2017-10-01","2018-10-01",morning),50, mode = "directed", weighted = TRUE)),
     layout = coord[cfg$names,],
     vertex.size = 4,
     vertex.label.cex= .1,
     edge.color = rgb(.8,.8,.8,.1))




