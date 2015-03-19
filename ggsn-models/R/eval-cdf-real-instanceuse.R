
library(ggplot2)
library(reshape2)
library(plyr)

#path = "/Users/cschwartz/Documents/paper/ggsn-results/full.csv"
source(file = "/home/fm/git/ggsn-models/R/plot_settings.R")
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
  y <- t(numcolwise(function(x) quantile(x, c(0.05,0.95)))(as.data.frame(t(apply(data, 1, cumsum)))))
  y <- y / norm
  colnames(y) <- c("q5", "q95")
  means <- cbind(x,y)
  
  means$N <- seq(1:nrow(means))
  means$max.tunnels <- max.tunnels
  means$max.instances <- max.instances
  means$start.up <- start.up
  df <- rbind(df, means)
}

# manually set quantiles?
#df[df$N == 30 & df$max.instances == 30 & df$max.tunnels == 75 & df$start.up == 300,]$q95 = 1.045
#df[df$N == 30 & df$max.instances == 30 & df$max.tunnels == 75 & df$start.up == 300,]$q5 = 1 - 0.045


dfsub <- subset(df, max.instances %in% c(30, 50))
dfsub <- subset(dfsub, max.tunnels %in% c(100, 150))
#dfsub <- subset(df, max.instances %in% c(30, 60))
#dfsub <- subset(dfsub, max.tunnels %in% c(75, 150))
dfsub <- subset(dfsub, start.up %in% c(300))


facet.label = function(variable, value) {
  sprintf("No. of servers: %s", as.character(value))
}
# detail
p <- ggplot(dfsub, aes(x=N,
                       y=mean, 
                       ymin=q5, 
                       ymax=q95
                       )) +
      geom_line(aes(colour=as.factor(max.tunnels))
               ) +
      geom_errorbar(
                    width=0.5) +
      facet_grid(max.instances ~ .,
                 space="free_x",
                 labeller = facet.label) +
      xlab(label_number_active_servers) +
      ylab(label_cdf) + 
      scale_color_manual(name = label_maximum_tunnels_per_server, values = colorPalette) +
      scale_linetype_discrete(name = label_startup_shutdown_time)


p <- saveFull(p, "instanceuse-multiserver-real.pdf")
print(p)
#ggsave("resourceusedistribution-detail-barplot.pdf")


## overall
#p <- ggplot(df, aes(x=N, y=mean, ymin=q5, ymax=q95)) + geom_bar(stat="identity", position="dodge")  + geom_errorbar(position="dodge", width=0.25) + facet_grid(max.instances ~ max.tunnels, scales="free_x", space="free_x")
#p + theme(text = element_text(size=18)) + ylab("relative duration") + xlab("number of active servers")
#ggsave("resourceusedistribution-overall-barplot.pdf", scale=3)
#
#
### mostly broken
#ggplot(df, aes(x=max.tunnels, y=N, fill=mean)) + geom_tile() + facet_wrap(~ max.instances)
#ggsave("resourceusedistribution-tileplot.pdf")





## file format:
# col 1: seed
# col 2: instance 0 (should always be 0)
# col -1 max instance duration

#path = "/Users/cschwartz/Documents/paper/ggsn-results/evaluateFeasibleTraditional/traditional/"
#files <- list.files(path = path, 
#                    pattern="instance_use_distribution.*csv")
#df <- data.frame()
#for (f in files) {
#  max.tunnels <- as.numeric(strsplit(f, "_")[[1]][4])
#  max.instances <- as.numeric(strsplit(f, "_")[[1]][5])
#  start.up <- 0
#  data <- read.table(sprintf("%s/%s", path, f), header=FALSE, sep=";")
#  
#  data <- data[,!(names(data) %in% c("V1", "V2"))]
#
#  x <- colMeans(data)
#  x <- melt(x)
#  x <- cumsum(x)
#  norm <- max(x)
#  x <- x / norm
#  colnames(x) <- "mean"
#  y <- t(numcolwise(function(x) quantile(x, c(0.05,0.95)))(as.data.frame(t(apply(data, 1, cumsum)))))
#  y <- y / norm
#  colnames(y) <- c("q5", "q95")
#  means <- cbind(x,y)
#  
#  means$N <- seq(1:nrow(means))
#  means$max.tunnels <- max.tunnels
#  means$max.instances <- max.instances
#  means$start.up <- start.up
#  df <- rbind(df, means)
#}

