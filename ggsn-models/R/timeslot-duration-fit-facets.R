source(file = "plot_settings.R")
library(parallel)
library(ggplot2)
path <- "/home/fm/git/eval-core/data"
d <- read.table(sprintf("%s/duration_activetunnels", path), header=FALSE)
colnames(d) <- c("ts_start", "ts_end")
d$duration <- d$ts_end - d$ts_start

d <-subset(d, ts_start != 4294967296 && ts_end != 4294967296) # data sanity

numpoints <- 1000
y <- seq(0,1,1/numpoints)
#y <- lseq(0.00001,1,numpoints) #alternatively: logspaced sequence
begintime <- 1302386400
d$hour_of_day <- floor(abs((d$ts_start-begintime)/3600)%%24)


## overall ecdf with color factor
sampled <- d[sample(nrow(d), nrow(d)*0.01), ]
ggplot(sampled, aes(x=duration, color=as.factor(hour_of_day))) + geom_line(stat="ecdf") + scale_x_log10("Tunnel duration (s)") + ylab("cumulative probability") + theme(text = element_text(size=20))  + guides(color=guide_legend("time of day", ncol=2, override.aes = list(size=4)))
ggsave("R-duration-timeofday-ecdf.pdf")
##



timeslots <- list(c(0:5), c(6:11), c(12:17), c(18:23))

df <- data.frame()

for (slot in timeslots){
  print(slot)
  
  t <- subset(d, hour_of_day %in% slot)
  x <- quantile(t$duration, probs=y)
  tmp <- data.frame(x=x,y=y, timeslot=paste(slot, collapse=""), origin="Measurement")
  #tmp <- subset(out, x>=0) # needed?
  df <- rbind(df, tmp)
}


x05h <- 0.919208 + (-110.707*y - 2289.94*y^3)/(y - 1.00469) - 60.6136*y - 3498.78*y^3
tmp <- data.frame(x=x05h,y=y, timeslot="0h-5h", origin="Fit")
df <- rbind(df, tmp)
x611h <- 1 + 117.484*y + -1720.13*y^4/(y - 1.0041) - 368.643*y^2
#x611h <- 68.94*y + -1035*y^4/(y - 1.002) + 2.332e4*y^13
tmp <- data.frame(x=x611h,y=y, timeslot="6h-11h", origin="Fit")
df <- rbind(df, tmp)
x1217h <- 0.952566 + 69.4907*y + (81146.1*y^3 + 1.08572e6*y^5)/(805 - 802.01*y)
tmp <- data.frame(x=x1217h,y=y, timeslot="12h-17h", origin="Fit")
df <- rbind(df, tmp)
x1823h <- 0.911924 + 82.0562*y + -2936.93*y^4/(1.94468*y - 1.9532)
#x1823h <- -4978.36*y/(81*y - 81.0087) + -2824.71*y^4/(1.93064*y - 1.94048)
tmp <- data.frame(x=x1823h,y=y, timeslot="18h-23h", origin="Fit")
df <- rbind(df, tmp)

df$timeslot[df$timeslot == "012345"] <- "0h-5h"
df$timeslot[df$timeslot == "67891011"] <- "6h-11h"
df$timeslot[df$timeslot == "121314151617"] <- "12h-17h"
df$timeslot[df$timeslot == "181920212223"] <- "18h-23h"


# 4 facet plot with corresponding fits
p <- ggplot(df, aes(x=x,
                    y=y,
                    color=as.factor(origin))) +
  #geom_point(size=.5) +
  geom_line() +
  scale_x_log10(name = label_tunnel_duration, limits = c(1, 1.5e6)) +
  facet_wrap(~timeslot) +
  ylab("CDF") +
  scale_colour_manual(name = "Distribution", values = colorPalette)

p <- saveFull(p, "timeslot-fits.pdf")
print(p)
#p + theme(text = element_text(size=20)) + ylab("cumulative probability") + xlab("tunnel duration (s)") + guides(color=guide_legend("", override.aes = list(size=4)))
#ggsave("timeslot-fits.pdf")


####### correlation tests
stringslots = list("0h-5h",  "6h-11h", "12h-17h", "18h-23h")
for (slot in stringslots){
  print(slot)
  s <- subset(df, timeslot == slot & origin=="Measurement")
  f <- subset(df, timeslot == slot & origin=="Fit")
  sq <- quantile(s$x, probs=seq(0, 1, by=0.1))
  fq <- quantile(f$x, probs=seq(0, 1, by=0.1))
  print(cor(sq,fq))
  print(cor.test(sq,fq))
}
