library(parallel)
library(emdbook) # lseq()

setwd("../eval-core/data")
#d <- read.table("duration_hours", header=FALSE)
d <- read.table("duration_activetunnels", header=FALSE)
colnames(d) <- c("ts_start", "ts_end")
d$duration <- d$ts_end - d$ts_start
d <-subset(d, ts_start != 4294967296 && ts_end != 4294967296) # data sanity
begintime <- 1302386400
d$hour_of_day <- floor(abs((d$ts_start-begintime)/3600)%%24)

numpoints <- 100000
y <- seq(0,1,1/numpoints)
#y <- lseq(0.00001,1,numpoints) alternatively: logspaced sequence


###############################################################################
## separate csv for every hour_of_day

for (i in 0:23){
  outfile <- paste(paste("duration-quantiles",sprintf("%d",i),sep="_"), ".csv", sep="")
  print(outfile)
  #y <- lseq(0.00001,1,numpoints) alternatively: logspaced sequence
  t <- subset(d, hour_of_day == i)
  x <- quantile(t$duration, probs=y)
  out <- data.frame(x=x,y=y)
  out <- subset(out, x>=0)
  write.table(out, outfile, row.names=FALSE, sep=" ", dec=".", quote=FALSE)
}
