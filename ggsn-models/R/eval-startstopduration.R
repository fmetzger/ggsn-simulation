library(ggplot2)

df <- data.frame()

path <- "/Users/cschwartz/Documents/paper/ggsn-results/evaluateFeasibleDimensioning/traditional/"
files <- list.files(path=path, pattern="metrics.*csv")
for (f in files){
  data <- read.table(sprintf("%s/%s", path, f), header=FALSE, colClasses = c("integer", "numeric", "numeric"),  col.names = c("seed", "res.util", "block.prob"), sep=";") 
  max.tunnels <- as.numeric(strsplit(f, "_")[[1]][2])
  block.prob.mean = mean(data$block.prob)
  block.prob.max = max(data$block.prob)
  block.prob.min = min(data$block.prob)
  res.util.mean = mean(data$res.util)
  res.util.min = min(data$res.util)
  res.util.max = max(data$res.util)
  data <- data.frame(startstop.duration = 20, res.util.mean = res.util.mean, res.util.min=res.util.min, res.util.max=res.util.max, max.tunnels=max.tunnels, block.prob.mean=block.prob.mean, block.prob.max=block.prob.max, block.prob.min=block.prob.min, max.instances=1)
  df <- rbind(df, data)
}

path <- "/home/fm/Documents/projekte/ggsn-sim/results/evaluateFeasibleMultiserver/multiserver/"
files <- list.files(path=path, pattern="metrics.*csv")
for (f in files){
  data <- read.table(sprintf("%s/%s", path, f), header=FALSE, colClasses = c("integer", "numeric", "numeric"),  col.names = c("seed", "res.util", "block.prob"), sep=";") 
  max.tunnels <- as.numeric(strsplit(f, "_")[[1]][2])
  max.instances <- as.numeric(strsplit(f, "_")[[1]][3])
  block.prob.mean = mean(data$block.prob)
  block.prob.max = max(data$block.prob)
  block.prob.min = min(data$block.prob)
  res.util.mean = mean(data$res.util)
  res.util.min = min(data$res.util)
  res.util.max = max(data$res.util)
  data <- data.frame(startstop.duration = 20, res.util.mean = res.util.mean, res.util.min=res.util.min, res.util.max=res.util.max, max.tunnels=max.tunnels, max.instances=max.instances, block.prob.mean=block.prob.mean, block.prob.max=block.prob.max, block.prob.min=block.prob.min)
  df <- rbind(df, data)
}

path <- "/Users/cschwartz/Documents/paper/ggsn-results/evaluateFeasibleStartStop/multiserver/"
files <- list.files(path=path, pattern="metrics.*csv")
for (f in files){
  data <- read.table(sprintf("%s/%s", path, f), header=FALSE, colClasses = c("integer", "numeric", "numeric"),  col.names = c("seed", "res.util", "block.prob"), sep=";") 
  max.tunnels <- as.numeric(strsplit(f, "_")[[1]][2])
  max.instances <- as.numeric(strsplit(f, "_")[[1]][3])
  startstop.duration <- as.numeric(strsplit(f, "_")[[1]][4])
  block.prob.mean = mean(data$block.prob)
  block.prob.max = max(data$block.prob)
  block.prob.min = min(data$block.prob)
  res.util.mean = mean(data$res.util)
  res.util.min = min(data$res.util)
  res.util.max = max(data$res.util)
  data <- data.frame(startstop.duration = startstop.duration, res.util.mean = res.util.mean, res.util.min=res.util.min, res.util.max=res.util.max, max.tunnels=max.tunnels, max.instances=max.instances, block.prob.mean=block.prob.mean, block.prob.max=block.prob.max, block.prob.min=block.prob.min)
  df <- rbind(df, data)
}

dfsub <- subset(df, max.instances == 100 & max.tunnels %in% c(20,40,60))
dfsub <- rbind(dfsub, subset(df, max.instances == 10 & max.tunnels %in% c(100,200,300,400,500)))
dfsub <- rbind(dfsub, subset(df, max.instances == 20 & max.tunnels %in% c(100,200,300)))
dfsub <- rbind(dfsub, subset(df, max.instances == 70 & max.tunnels %in% c(25,50,75)))

## blocking probability barchart
p <- ggplot(dfsub, aes(x= max.tunnels, y= block.prob.mean, ymax = block.prob.max, ymin=block.prob.min, fill=as.factor(startstop.duration))) + geom_bar(stat="identity", position="dodge", width=10) + geom_errorbar(position="dodge", width=10) + facet_wrap(~ max.instances, scales="free_x") + scale_y_continuous(limits=c(0,1))
p + theme(text = element_text(size=20)) + ylab("blocking probability") + xlab("supported tunnels per instance") + guides(fill=guide_legend("start/stop\nduration"))
ggsave("startstopduration-blockingprobability-barchart.pdf")

## resource utilization bar chart
p <- ggplot(dfsub, aes(x= max.tunnels, y = res.util.mean, ymax = res.util.max, ymin=res.util.min, fill=as.factor(startstop.duration))) + geom_bar(stat="identity", position="dodge", width=10) + geom_errorbar(position="dodge", width=10) + facet_wrap(~ max.instances, scales="free_x")
p + theme(text = element_text(size=20)) + ylab("tunnel occupation") + xlab("supported tunnels per instance") + guides(fill=guide_legend("start/stop\nduration"))
ggsave("startstopduration-resutilization-barchart.pdf")
