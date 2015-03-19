library(ggplot2)

df <- data.frame()

path <- "/Users/cschwartz/Documents/paper/ggsn-results/evaluateFeasibleDimensioning/traditional/"
files <- list.files(path = path, pattern="metrics.*csv")
for (f in files){
  data <- read.table(sprintf("%s/%s", path, f), header=FALSE, colClasses = c("integer", "numeric", "numeric"),  col.names = c("seed", "res.util", "block.prob"), sep=";") 
  max.tunnels <- as.numeric(strsplit(f, "_")[[1]][2])
  block.prob.mean = mean(data$block.prob)
  block.prob.max = quantile(data$block.prob, 0.95)
  block.prob.min = quantile(data$block.prob, 0.05)
  res.util.mean = mean(data$res.util)
  res.util.min = quantile(data$res.util, 0.05)
  res.util.max = quantile(data$res.util, 0.95)
  data <- data.frame(res.util.mean = res.util.mean, res.util.min=res.util.min, res.util.max=res.util.max, max.tunnels=max.tunnels, block.prob.mean=block.prob.mean, block.prob.max=block.prob.max, block.prob.min=block.prob.min, max.instances=1)
  
  df <- rbind(df, data)
}


path <- "/Users/cschwartz/Documents/paper/ggsn-results/evaluateFeasibleMultiserver/multiserver/"
files <- list.files(path = path, pattern="metrics.*csv")
for (f in files){
  data <- read.table(sprintf("%s/%s", path, f), header=FALSE, colClasses = c("integer", "numeric", "numeric"),  col.names = c("seed", "res.util", "block.prob"), sep=";") 
  max.tunnels <- as.numeric(strsplit(f, "_")[[1]][2])
  max.instances <- as.numeric(strsplit(f, "_")[[1]][3])
  block.prob.mean = mean(data$block.prob)
  block.prob.max = quantile(data$block.prob, 0.95)
  block.prob.min = quantile(data$block.prob, 0.95)
  res.util.mean = mean(data$res.util)
  res.util.min = quantile(data$res.util, 0.05)
  res.util.max = quantile(data$res.util, 0.95)
  #res.util=mean(data$res.util)
  data <- data.frame(res.util.mean = res.util.mean, res.util.min=res.util.min, res.util.max=res.util.max, max.tunnels=max.tunnels, max.instances=max.instances, block.prob.mean=block.prob.mean, block.prob.max=block.prob.max, block.prob.min=block.prob.min)
  df <- rbind(df, data)
}

summary(df$block.prob.mean)
summary(df$block.prob.max)
summary(df$res.util)

#ggplot(df, aes(x=max.instances*max.tunnels, y=block.prob.mean)) + geom_point() + scale_x_discrete(breaks=seq(0,1000,50))
#ggsave("evaluateFeasibleDimensioning.pdf")


p <- ggplot(df, aes(x=max.tunnels * max.instances, y=block.prob.mean, ymin=block.prob.min, ymax=block.prob.max, color=as.factor(max.instances))) + geom_point(size=3) + geom_errorbar(width=100) + coord_cartesian(xlim=c(0,5500))
p + theme(text = element_text(size=20)) + ylab("blocking probability") + xlab("total supported tunnels") + guides(colour=guide_legend("supported \ninstances"))
ggsave("feasiblemultiserver-blockprob.pdf")


p <- ggplot(df, aes(x=max.tunnels * max.instances, y=res.util.mean, ymax = res.util.max, ymin=res.util.min, color=as.factor(max.instances))) +  geom_point(size=3) + geom_errorbar(width=100) + geom_abline(intercept=0) + coord_cartesian(xlim=c(0,10000))
p + theme(text = element_text(size=20)) + ylab("tunnel occupation") + xlab("total supported tunnels") + guides(colour=guide_legend("supported \ninstances"))
ggsave("feasiblemultiserver-resutil.pdf")
