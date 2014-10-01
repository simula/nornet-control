source("plotter.R")

data <- loadResults("passive.flow-ReceivedBytes.data.bz2")

filter <- (data$FromSite == 9) & (data$ToSite == 2)

d <- subset(data, filter)
