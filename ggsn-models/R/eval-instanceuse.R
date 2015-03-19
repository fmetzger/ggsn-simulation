library(ggplot2)
library(reshape)



## file format:
# col 1: seed
# col 2: instance 0 (should always be 0)
# col -1 max instance duration

setwd("/home/fm/Documents/projekte/ggsn-sim/results/evaluateFeasibleMultiserver/multiserver/")
files <- list.files(pattern="instance_use_distribution.*csv")
df <- data.frame()
for (f in files) {
  max.tunnels <- as.numeric(strsplit(f, "_")[[1]][4])
  max.instances <- as.numeric(strsplit(f, "_")[[1]][5])
  data <- read.table(f, header=FALSE, sep=";")
  
  # drop seed and 0 instances
   data <- data[,!(names(data) %in% c("V1", "V2"))]
  #data <- data[,!(names(data) %in% c("V1"))]

  x <- colMeans(data)
  x <- melt(x)
  colnames(x) <- "mean"
  y <- t(numcolwise(function(x) quantile(x, c(0.05,0.95)))(data))
  colnames(y) <- c("q5", "q95")
  means <- cbind(x,y)
  
  # filter only the trailing (not the leading) rows with mean zero
  tmp <- means$mean
  index <- 0
  for (row in rev(tmp)) {
    if(row == 0){
      index <- index + 1
    }
    else {
      break
    }
  }
  threshold <- max.instances - index
  print(paste(max.instances, max.tunnels, threshold))
  means <- means[rownames(means) %in% paste("V", seq(1:(threshold+2)), sep=""),]
  
  if(nrow(means) != 0) {
    means$N <- seq(1:nrow(means))
    means$max.tunnels <- max.tunnels
    means$max.instances <- max.instances

    df <- rbind(df, means)
  }
    else {
      print("zero rows")
    }
}

dfsub <- subset(df, max.instances %in% c(30, 60))
dfsub <- subset(dfsub, max.tunnels %in% c(150,300))

# detail
p <- ggplot(dfsub, aes(x=N, y=mean, ymin=q5, ymax=q95)) + geom_bar(stat="identity", position="dodge") + geom_errorbar(position="dodge", width=0.25) + facet_grid(max.instances ~ max.tunnels,  space="free_x")
p + theme(text = element_text(size=20)) + ylab("relative duration") + xlab("number of occupied servers")
ggsave("resourceusedistribution-detail-barplot.pdf")


# overall
p <- ggplot(df, aes(x=N, y=mean, ymin=q5, ymax=q95)) + geom_bar(stat="identity", position="dodge")  + geom_errorbar(position="dodge", width=0.25) + facet_grid(max.instances ~ max.tunnels, scales="free_x", space="free_x")
p + theme(text = element_text(size=18)) + ylab("relative duration") + xlab("number of active servers")
ggsave("resourceusedistribution-overall-barplot.pdf", scale=3)


## mostly broken
ggplot(df, aes(x=max.tunnels, y=N, fill=mean)) + geom_tile() + facet_wrap(~ max.instances)
ggsave("resourceusedistribution-tileplot.pdf")