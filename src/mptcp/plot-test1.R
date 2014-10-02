source("plotter.R")

data <- loadResults("passive.flow-ReceivedBytes.data.bz2")


getColor <- function(originalGain, minPercent, maxPercent)
{
   if(is.na(originalGain)) {
      return("white")
   }
   gainPercent <- round(originalGain) 
   if(gainPercent < minPercent) {
      gainPercent <- minPercent
   }
   if(gainPercent > maxPercent) {
      gainPercent <- maxPercent
   }
   range      <- maxPercent - minPercent
   colorRange <- rainbow(range + 1)
   color <- colorRange[max(1, gainPercent + -(minPercent))]
   return(color)
}


filter <- (data$IPVersion == 4)

d <- subset(data, filter)

xTitle <- "Source Endpoint"
xSet   <- factor(d$FromProviderIndex * 256 + d$FromSiteIndex)
yTitle <- "Destination Endpoint"
ySet   <- factor(d$ToProviderIndex * 256 + d$ToSiteIndex)

zTitle <- "Multi-Path Transport Gain Factor [1]"

x <- c()
y <- c()
z <- c()
f <- c()
for(ipVersion in levels(factor(d$IPVersion))) {
   xLevel <- 1
   for(xValue in levels(xSet)) {
      yLevel <- 1
      for(yValue in levels(ySet)) {
         mptcp <- subset(d, (xSet == xValue) & (ySet == yValue) & (d$CMT == "mptcp") & (d$IPVersion == ipVersion))
         tcp   <- subset(d, (xSet == xValue) & (ySet == yValue) & (d$CMT == "off") & (d$IPVersion == ipVersion))

         mptcpMean <- mean(mptcp$passive.flow.ReceivedBytes)
         tcpMean   <- mean(tcp$passive.flow.ReceivedBytes)
         zValue <- (mptcpMean - tcpMean) / tcpMean
         
         if(!is.na(zValue)) {
            if(zValue < 0.8) {
               fValue <- "gray"
            }
            else {
               fValue <- getColor(100.0 * zValue, -200.0, 300.0)
            }
            
            x <- append(x, xLevel)
            y <- append(y, yLevel)
            z <- append(z, zValue)
            f <- append(f, fValue)
         }

         yLevel <- yLevel + 1
      }
      xLevel <- xLevel + 1
   }
}

pdf("test1.pdf", width=15, height=10, family="Helvetica", pointsize=22)
scatterplot3d(x, y, z, highlight.3d=FALSE, color=f,
 xlab=xTitle, ylab=yTitle, zlab=zTitle,
 col.axis="blue", col.grid="lightblue", type="h",
 pch=20)
dev.off()
