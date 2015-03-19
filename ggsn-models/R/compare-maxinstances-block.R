source(file = "plot_settings.R")

data <- read.table('metrics.csv', sep = ',', header = TRUE) 
data$total.tunnels = data$max.tunnels * data$max.instances
data$max.tunnels = factor(data$max.tunnels)
data$startstop.duration = factor(data$startstop.duration)

data <- subset(data, total.tunnels == 5000 &
                     max.instances %in% c(10, 50, 100))

data$max.instances = factor(data$max.instances)
data$max.tunnels = factor(data$max.tunnels, c(500, 100, 50))

data <- summarySE(data, measurevar = "block.prob", groupvars = c("max.instances", "max.tunnels", "startstop.duration"))
label_full_name <- function(variable, values) {
  sprintf("Maximum number of instances: %s", as.character(values))
}

p <- ggplot(data, aes(x = max.tunnels,
                      y = block.prob,
                      color = startstop.duration)) +
      geom_point() +
      geom_errorbar(aes(ymin = block.prob - ci, ymax = block.prob + ci), width = 0.1) +
      geom_line(aes(group = startstop.duration)) +
      scale_x_discrete(name = label_maximum_tunnels_per_server) +
      scale_y_continuous(name = label_blocking_probability) +
      scale_colour_manual(name = label_startup_shutdown_time,
                          values = colorPalette,
                          guide = guide_legend(nrow = 2))

p <- saveFull(p, "compare-maxinstances-block.pdf")
print(p)
