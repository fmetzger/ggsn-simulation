source(file = "plot_settings.R")
require("pracma")

data <- read.table('../../ggsn-data/duration_activetunnels', col.names = c("timestamp", "duration"))

#load("activetunnel-duration")
shortest.duration <- min(data$duration)
longest.duration <- max(data$duration)

x <- logseq(shortest.duration, longest.duration, 10000)
cdf <- ecdf(data$duration)
y <- cdf(x)

f <- function(x) { (1948*x + x^2)/(1.223e5 + 3206*x + x^2) }
f.inverted <- function(y) { 3.8147e-6/(y-1) * (2.55328e8 -4.20217e8*y - sqrt(6.51925e16-2.06182e17*y + 1.68178e17*y^2)) }

plot.ecdf(data$duration, xlim=c(0.01,longest.duration), log = "x")
lines(x, f(x), col="green")
lines(f.inverted(y), y, col="red")


