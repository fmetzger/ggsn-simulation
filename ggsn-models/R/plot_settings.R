library(ggplot2)
library(grid)
library(reshape2)

figure_path = "../tex/figures"

label_total_supported_tunnels = "Total supported tunnels"
label_blocking_probability = "Blocking probability"
label_relative_blocking_probability = "Rel. increase of\n blocking probability"
label_max_instances = "Max. number of instances"
label_number_active_servers = "Number of active servers"
label_cdf = "CDF"
label_maximum_tunnels_per_server = "Max. number of tunnels per server"
label_startup_shutdown_time = "Start up and\nshut down time"
label_mean_resource_utilization = "Mean resource utilization"
label_tunnel_duration <- "Tunnel duration (s)"

colorPalette <- c("#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

theme_set(theme_grey(base_size = 10)) 

imageWidth <- 8
imageFullHeight <- imageWidth / 4.0 * 3.0
imageHalfHeight <- imageFullHeight / 1.5

units <- "cm"

plot_options <- theme(legend.key.height = unit(0.5, units),
                      plot.margin = unit(c(0, 0, 0, 0), units),
                      legend.margin = unit(-0.6, units),
                      legend.position = "bottom",
                      legend.direction = "horizontal",
                      legend.box = "vertical",
                      legend.key.height = unit(0, units))

cropPdf <- function(filename) {
  system(sprintf("pdfcrop %s %s", filename, filename))
}

savePlot <- function(plot,  filename, height) {
  plot <- plot + plot_options
  filename <- sprintf("%s/%s", figure_path, filename)
  ggsave(filename, plot = plot,
                   height = height,
                   width = imageWidth,
                   units = units)
  cropPdf(filename)
  plot
}

saveHalf <- function(plot, filename) {
  savePlot(plot, filename, imageHalfHeight)
}

saveFull <- function(plot, filename) {
  savePlot(plot, filename, imageFullHeight)
}

saveDouble <- function(plot, filename) {
  plot <- plot + plot_options
  filename <- sprintf("%s/%s", figure_path, filename)
  ggsave(filename, plot = plot,
                   height = imageFullHeight,
                   width = 2*imageWidth,
                   units = units)
  cropPdf(filename)
  plot
}

summarySE <- function(data=NULL, measurevar, groupvars=NULL, na.rm=FALSE,
                      conf.interval=.95, .drop=TRUE) {
    require(plyr)

    # New version of length which can handle NA's: if na.rm==T, don't count them
    length2 <- function (x, na.rm=FALSE) {
        if (na.rm) sum(!is.na(x))
        else       length(x)
    }

    # This does the summary. For each group's data frame, return a vector with
    # N, mean, and sd
    datac <- ddply(data, groupvars, .drop=.drop,
      .fun = function(xx, col) {
        c(N    = length2(xx[[col]], na.rm=na.rm),
          mean = mean   (xx[[col]], na.rm=na.rm),
          sd   = sd     (xx[[col]], na.rm=na.rm)
        )
      },
      measurevar
    )

    # Rename the "mean" column    
    datac <- rename(datac, c("mean" = measurevar))

    datac$se <- datac$sd / sqrt(datac$N)  # Calculate standard error of the mean

    # Confidence interval multiplier for standard error
    # Calculate t-statistic for confidence interval: 
    # e.g., if conf.interval is .95, use .975 (above/below), and use df=N-1
    ciMult <- qt(conf.interval/2 + .5, datac$N-1)
    datac$ci <- datac$se * ciMult

    return(datac)
}
