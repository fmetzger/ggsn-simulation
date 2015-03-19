source(file = "plot_settings.R")

df <- data.frame()

path = "/Users/cschwartz/Documents/paper/ggsn-results/evaluateFeasibleDimensioning/traditional"

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
  data <- data.frame(res.util.mean = res.util.mean, res.util.min=res.util.min, res.util.max=res.util.max, max.tunnels=max.tunnels, block.prob.mean=block.prob.mean, block.prob.max=block.prob.max, block.prob.min=block.prob.min, max.instances=1, startstop.duration = 0, total.tunnels = max.tunnels)
  
  df <- rbind(df, data)
}

path = "/Users/cschwartz/Documents/paper/ggsn-results/full.csv"

files <- list.files(path = path, pattern="metrics.*csv")
for (f in files){
  data <- read.table(sprintf("%s/%s", path, f), header=FALSE, colClasses = c("integer", "numeric", "numeric"),  col.names = c("seed", "res.util", "block.prob"), sep=";") 
  max.tunnels <- as.numeric(strsplit(f, "_")[[1]][2])
  max.instances <- as.numeric(strsplit(f, "_")[[1]][3])
  total.tunnels <- max.tunnels * max.instances
  startstop.duration <- as.numeric(strsplit(f, "_")[[1]][4])
  block.prob.mean = mean(data$block.prob)
  block.prob.max = quantile(data$block.prob, 0.95)
  block.prob.min = quantile(data$block.prob, 0.05)
  res.util.mean = mean(data$res.util)
  res.util.min = quantile(data$res.util, 0.05)
  res.util.max = quantile(data$res.util, 0.95)
  data <- data.frame(res.util.mean = res.util.mean, res.util.min=res.util.min, res.util.max=res.util.max, max.tunnels=max.tunnels, block.prob.mean=block.prob.mean, block.prob.max=block.prob.max, block.prob.min=block.prob.min, max.instances=max.instances, startstop.duration = startstop.duration, total.tunnels = total.tunnels)
  
  df <- rbind(df, data)
}



df = subset(df, max.instances %in% c(1, 30, 60) &
                startstop.duration %in% c(0, 300) &
                total.tunnels == 4500)
df$max.tunnels = factor(df$max.tunnels, c(4500, 150, 75))
df$max.instances = factor(df$max.instances)
df$relative.blocking.probability <- df$block.prob.mean / subset(df, max.instances == 1)$block.prob.mean
df$relative.blocking.probability.max <- df$block.prob.max / subset(df, max.instances == 1)$block.prob.mean
df$relative.blocking.probability.min <- df$block.prob.min / subset(df, max.instances == 1)$block.prob.mean

p <- ggplot(df, aes(x=max.tunnels,
                    y=relative.blocking.probability,
                    ymin=relative.blocking.probability.min,
                    ymax=relative.blocking.probability.max)) +
            geom_point(stat = "identity") +
            geom_errorbar(width=1) +
            scale_x_discrete() +
            scale_y_continuous(limits = c(0, 2)) +
            xlab(label_maximum_tunnels_per_server) +
            ylab(label_relative_blocking_probability)

#p <- p + theme(text = element_text(size=20)) + ylab("Blocking probability") + xlab("Total supported tunnels")
p <- saveHalf(p, "blocking-comparison.pdf")
print(p)

