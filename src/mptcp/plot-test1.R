source("plotter.R")

data <- loadResults("passive.flow-ReceivedBytes.data.bz2")



filter <- (data$CMT == "mptcp") & (data$IPVersion == 4) & (data$FromProviderIndex == 1) & (data$ToProviderIndex == 1)
d <- subset(data, filter)


x <- d$FromSiteIndex
y <- d$ToSiteIndex
z <- d$passive.flow.ReceivedBytes / (1024 * 1024)

scatterplot3d(x, y, z, highlight.3d=TRUE,
 col.axis="blue", col.grid="lightblue",
 main="scatterplot3d - 2", pch=20)