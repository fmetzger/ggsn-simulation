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
#y <- seq(0,1,1/numpoints)
y <- lseq(0.00001,1,numpoints) # alternatively: logspaced sequence


###############################################################################
# also create combined output for each 6h block, starting at 0

timeslots <- list(c(0:5), c(6:11), c(12:17), c(18:23))

for (slot in timeslots){
  outfile <- paste(paste("duration-quantiles-logspace",paste(slot, collapse=""),sep="_"), ".csv", sep="")
  print(outfile)
  #y <- lseq(0.00001,1,numpoints) alternatively: logspaced sequence
  t <- subset(d, hour_of_day %in% slot)
  x <- quantile(t$duration, probs=y)
  out <- data.frame(x=x,y=y)
  out <- subset(out, x>=0)
  write.table(out, outfile, row.names=FALSE, sep=" ", dec=".", quote=FALSE)
}