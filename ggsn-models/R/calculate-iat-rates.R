#!/usr/bin/env R

require(fitdistrplus)

load.data <- function(filename) {
  data <- read.table(filename, header=FALSE, colClasses = c("numeric", "integer", "NULL", "NULL"),  col.names = c("ts", "hour.of.day", "NULL", "NULL"), fill=TRUE) ## only active tunnels

  data <-subset(data, ts >= 1302472800) # drop everything before 1302472800 epoch// Mo 11. Apr 00:00:00 CEST 2011 as we dont have real tunnel arrivals before that
  data <-subset(data, ts != 4294967296) # drop the 2^32 artifacts (where teh heck do they even come from?)
  data$iat <- c(NA, diff(data$ts)) # add the diff column with NA in the first row
  data<- subset(data, !is.na(iat)) # filter empty diff rows
  data <- subset(data, iat < 60*60) # iats larger than one hour only occur due to measurement errors if slots of one hour are considered
  data
}

fit.by.hour <- function(hour, records) {
  current.records <- subset(records, hour.of.day == hour)
  iat.fit <- fitdist(current.records$iat, 'exp')
  as.numeric(iat.fit$estimate["rate"])
}

write.results <-  function(hours, filename) {
  result <- data.frame(hour.of.day = hours, rates = as.numeric(rates))
  write.table(result, filename, sep = ";", row.names = FALSE)
}

hours <- seq(0, 23)
records <- load.data("../../ggsn-data/ts_create_active_hours")
rates <- lapply(hours, fit.by.hour, records)
write.results(hours, "../simulation/assets/interarrival_rates.csv")

