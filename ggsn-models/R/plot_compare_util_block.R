source(file = "plot_settings.R")

data <- read.table('metrics.csv', sep = ',', header = TRUE) 
data$total.tunnels = data$max.tunnels * data$max.instances
data$max.tunnels = factor(data$max.tunnels)
data$max.instances = factor(data$max.instances)
data$startstop.duration = factor(data$startstop.duration)

data <- subset(data, total.tunnels <= 5000 &
                      startstop.duration %in% c(60, 300) &
                      max.instances %in% c(40, 100))

label_full_name <- function(variable, values) {
  sprintf("Maximum number of instances: %s", as.character(values))
}

p <- ggplot(data, aes(x = res.util,
                      y = block.prob,
                      shape = max.tunnels,
                      color = startstop.duration)) +
      geom_point() +
      facet_grid(~ max.instances, labeller = label_full_name) +
      scale_x_continuous(name = label_mean_resource_utilization) +
      scale_y_log10(name = label_blocking_probability) +
      scale_shape_manual(name = label_maximum_tunnels_per_server,
                         values = seq(1, 7),
                         guide = guide_legend(nrow = 1)) +
      scale_colour_manual(name = label_startup_shutdown_time,
                          values = colorPalette)

p <- saveDouble(p, "compare-util-block.pdf")
  
print(p)
