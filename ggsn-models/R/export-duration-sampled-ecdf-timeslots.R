library(parallel)

setwd("../eval-core/data")
#d <- read.table("duration_hours", header=FALSE)
d <- read.table("duration_activetunnels", header=FALSE)
colnames(d) <- c("ts_start", "ts_end")
d$duration <- d$ts_end - d$ts_start
d <-subset(d, ts_start != 4294967296 && ts_end != 4294967296) # data sanity
begintime <- 1302386400
d$hour_of_day <- floor(abs((d$ts_start-begintime)/3600)%%24)


timeslots <- list(c(0:5), c(6:11), c(12:17), c(18:23))

for (slot in timeslots){
  print(slot)
  ##
  metric <- 0
  t <- subset(d, hour_of_day %in% slot)
  while (metric < 0.95){
    d.sampled <- t[sample(nrow(t), 10000),  ]
    metric <- ks.test(t$duration, d.sampled$duration)$p.value
    print(metric)
  }
  fn <- ecdf(d.sampled$duration)
  out <- data.frame(x=d.sampled$duration, y=fn(d.sampled$duration))
  outfile <- paste(paste("duration-sampled-ecdf",paste(slot, collapse=""),sep="_"), ".csv", sep="")
  print(outfile)
  write.table(out, outfile, row.names=FALSE, sep=" ", dec=".", quote=FALSE)
}
