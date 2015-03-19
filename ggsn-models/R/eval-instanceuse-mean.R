library(ggplot2)
library(reshape)



## file format:
# col 1: seed
# col 2: instance 0 (should always be 0)
# col -1 max instance duration

setwd("/home/fm/Documents/projekte/ggsn-sim/results/evaluateFeasibleMultiserver/multiserver/")
files <- list.files(pattern="instance_use_distribution.*csv")
dfwm <- data.frame()
for (f in files) {
  max.tunnels <- as.numeric(strsplit(f, "_")[[1]][4])
  max.instances <- as.numeric(strsplit(f, "_")[[1]][5])
  data <- read.table(f, header=FALSE, sep=";")
  data <- data[,!(names(data) %in% c("V1", "V2"))] # drop seed and 0 instances
   
  # calculate the mean number of active instances per experiment seed
  # do only if df contains at least one value > 0
  if(any(sapply(data, function(x) any(x > 0)))){
    x <- apply(data, 1, function(x) weighted.mean(seq(1:ncol(data)), x) / max.instances)
    x <- melt(x)
    wm <- mean(x$value)
    y <- quantile(x$value, c(0.05, 0.95))
    
    tmp <- data.frame(startstop.duration=20, max.tunnels = max.tunnels, max.instances = max.instances, rel.instance.use = wm, q5.instance.use = y[["5%"]], q95.instance.use = y[["95%"]])
    dfwm <- rbind(dfwm, tmp)
  }
} 

p <- ggplot(dfwm, aes(x=max.tunnels, y=rel.instance.use, ymin=q5.instance.use, ymax=q95.instance.use)) + geom_line() + geom_point() + geom_errorbar() + facet_wrap(~ max.instances, scale="free") + ylim(0,1)
p + theme(text = element_text(size=20)) + ylab("mean relative number of instances in use") + xlab("supported tunnels per instance") + guides(color=guide_legend("start/stop\nduration"))
ggsave("instanceuse-mean.pdf")

setwd("/home/fm/Documents/projekte/ggsn-sim/results/evaluateFeasibleStartStop/multiserver/")
files <- list.files(pattern="instance_use_distribution.*csv")
for (f in files) {
  max.tunnels <- as.numeric(strsplit(f, "_")[[1]][4])
  max.instances <- as.numeric(strsplit(f, "_")[[1]][5])
  startstop.duration <- as.numeric(strsplit(f, "_")[[1]][6])
  data <- read.table(f, header=FALSE, sep=";")
  data <- data[,!(names(data) %in% c("V1", "V2"))] # drop seed and 0 instances
  
  # calculate the mean number of active instances per experiment seed
  # do only if df contains at least one value > 0
  if(any(sapply(data, function(x) any(x > 0)))){
    x <- apply(data, 1, function(x) weighted.mean(seq(1:ncol(data)), x) / max.instances)
    x <- melt(x)
    wm <- mean(x$value)
    y <- quantile(x$value, c(0.05, 0.95))
    
    tmp <- data.frame(startstop.duration = startstop.duration, max.tunnels = max.tunnels, max.instances = max.instances, rel.instance.use = wm, q5.instance.use = y[["5%"]], q95.instance.use = y[["95%"]])
    dfwm <- rbind(dfwm, tmp)
  }
} 

#dfsub <- subset(dfwm, max.instances == 10 & max.tunnels %in% c(100,200,300,400,500,600,700))
#dfsub <- rbind(dfsub, subset(dfwm, max.instances == 20 & max.tunnels %in% c(100,200,300)))
#dfsub <- rbind(dfsub, subset(dfwm, max.instances == 30 & max.tunnels <= 300))
#dfsub <- rbind(dfsub, subset(dfwm, max.instances == 40 & max.tunnels < 250))
#dfsub <- rbind(dfsub, subset(dfwm, max.instances == 50 & max.tunnels < 250))
#dfsub <- rbind(dfsub, subset(dfwm, max.instances == 60 & max.tunnels < 200))
#dfsub <- rbind(dfsub, subset(dfwm, max.instances == 70 & max.tunnels < 120))
#dfsub <- rbind(dfsub, subset(dfwm, max.instances == 80 & max.tunnels <= 100))
#dfsub <- rbind(dfsub, subset(dfwm, max.instances == 90 & max.tunnels %in% c(20,40,60,80)))
#dfsub <- rbind(dfsub, subset(dfwm, max.instances == 100 & max.tunnels < 250))

dfsub <- subset(dfwm, max.instances == 10 & max.tunnels %in% c(100,200,300,400,500))
dfsub <- rbind(dfsub, subset(dfwm, max.instances == 20 & max.tunnels %in% c(100,200,300)))
dfsub <- rbind(dfsub, subset(dfwm, max.instances == 70 & max.tunnels %in% c(25,50,75)))
dfsub <- rbind(dfsub, subset(dfwm, max.instances == 90 & max.tunnels %in% c(20,40,60)))

p <- ggplot(dfsub, aes(x=max.tunnels, y=rel.instance.use, ymin=q5.instance.use, ymax=q95.instance.use, color=as.factor(startstop.duration))) + geom_line() + geom_point() + geom_errorbar() + facet_wrap(~ max.instances, scale="free") + ylim(0,1)
p + theme(text = element_text(size=20)) + ylab("mean relative number of instances in use") + xlab("supported tunnels per instance") + guides(color=guide_legend("start/stop\nduration"))
ggsave("instanceuse-startstop-mean.pdf")
