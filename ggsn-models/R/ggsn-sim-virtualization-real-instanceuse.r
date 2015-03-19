library(ggplot2)
library(reshape2)
library(plyr)

path <- "/home/fm/Documents/projekte/ggsn-sim/results/combined/"

files <- list.files(path = path, pattern="instance_use_distribution.*csv")

df <- data.frame()
for (f in files) {
  max.tunnels <- as.numeric(strsplit(f, "_")[[1]][4])
  max.instances <- as.numeric(strsplit(f, "_")[[1]][5])
  start.up <- as.numeric(strsplit(f, "_")[[1]][6])
  data <- read.table(sprintf("%s/%s", path, f), header=FALSE, sep=";")
  
  data <- data[,!(names(data) %in% c("V1", "V2"))]

  x <- colMeans(data)
  x <- melt(x)
  x <- cumsum(x)
  norm <- max(x)
  x <- x / norm
  colnames(x) <- "mean"
  
  # 95% quantiles
  y <- t(numcolwise(function(x) quantile(x, c(0.05,0.95)))(as.data.frame(t(apply(data, 1, cumsum)))))
  y <- y / norm
  colnames(y) <- c("q5", "q95")
  
  # 95% confidence intervals
  sdev <- t(numcolwise(function(x) sd(x))(as.data.frame(t(apply(data, 1, cumsum)))))
  colnames(sdev) <- "stddev"
  sample.size <- nrow(data)
  error <- qnorm(0.975)*sdev/sqrt(sample.size)
  left  <- x-error
  colnames(left) <- "left"
  right <- x+error
  colnames(right) <- "right"
  means <- cbind(x,y,sdev,left,right)
  
  means$N <- seq(1:nrow(means))
  means$max.tunnels <- max.tunnels
  means$max.instances <- max.instances
  means$start.up <- start.up
  df <- rbind(df, means)
}

dfsub <- subset(df, max.instances %in% c(30, 50))
dfsub <- subset(dfsub, max.tunnels %in% c(100, 150))
#dfsub <- subset(df, max.instances %in% c(30, 60))
#dfsub <- subset(dfsub, max.tunnels %in% c(75, 150))
dfsub <- subset(dfsub, start.up %in% c(300))


facet.label = function(variable, value) {
  sprintf("%s instances", as.character(value))
}
p <- ggplot(dfsub, aes(x=N,y=mean,ymin=left,ymax=right)) + geom_line(aes(colour=as.factor(max.tunnels)))
p <- p + geom_errorbar(width=0.5) + facet_grid(max.instances ~ .,space="free_x",labeller = facet.label)
p <- p + xlab("number of active servers") + ylab("cumulative probability")
p + theme(text = element_text(size=20)) +  theme(legend.position="bottom") + guides(colour=guide_legend("tunnel capacity per instance"))
ggsave("R-virtualized-instanceuse.pdf", width=12, height=10)

