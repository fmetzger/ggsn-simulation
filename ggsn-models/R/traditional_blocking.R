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
  data <- data.frame(res.util.mean = res.util.mean, res.util.min=res.util.min, res.util.max=res.util.max, max.tunnels=max.tunnels, block.prob.mean=block.prob.mean, block.prob.max=block.prob.max, block.prob.min=block.prob.min, max.instances=1)
  
  df <- rbind(df, data)
}

df$max.instances = factor(df$max.instances)

acceptable.tunnel.count = df[with(df, order(max.tunnels)), ]

p <- ggplot(df, aes(x=max.tunnels,
                    y=block.prob.mean,
                    ymin=block.prob.min,
                    ymax=block.prob.max)) +
            geom_line() +
            geom_errorbar(width=100) +
            coord_cartesian(xlim=c(0,5500), ylim = c(-0.1, 1.1)) +
            xlab(label_total_supported_tunnels) +
            ylab(label_blocking_probability)

#p <- p + theme(text = element_text(size=20)) + ylab("Blocking probability") + xlab("Total supported tunnels")
p <- saveHalf(p, "traditional-blocking.pdf")
print(p)

