library(scatterplot3d)
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
zTitle <- "Multi-Path Transport Gain Factor in Log Scale [1]"


cat("X-Legend:\n")
xLevel <- 1
for(xValue in levels(xSet)) {
   filter <- (xSet == xValue)
   r <- subset(d, filter)
   provider = levels(factor(r$FromProvider))[1]
   site     = unlist(levels(factor(r$FromSite))[1])
   cat(sep="\t", xLevel, provider, site, "\n")
   xLevel <- xLevel + 1
}

cat("Y-Legend:\n")
yLevel <- 1
for(yValue in levels(ySet)) {
   filter <- (ySet == yValue)
   r <- subset(d, filter)
   provider = levels(factor(r$ToProvider))[1]
   site     = unlist(levels(factor(r$ToSite))[1])
   cat(sep="\t", yLevel, provider, site, "\n")
   yLevel <- yLevel + 1
}


x <- c()
y <- c()
z <- c()
f <- c()
for(ipVersion in levels(factor(d$IPVersion))) {
   xLevel <- 1
   for(xValue in levels(xSet)) {
      yLevel <- 1
      for(yValue in levels(ySet)) {
         filter <- (xSet == xValue) & (ySet == yValue) & (d$IPVersion == ipVersion)
         mptcp <- subset(d, filter & (d$CMT == "mptcp"))
         tcp   <- subset(d, filter & (d$CMT == "off"))

         mptcpMean <- mean(mptcp$passive.flow.ReceivedBytes)
         tcpMean   <- mean(tcp$passive.flow.ReceivedBytes)
         zValue <- mptcpMean / tcpMean

         if(!is.na(zValue) && (zValue > 0.0)) {

#             if(zValue > 10) {
#                zValue <- 10
#             }

            if(zValue < 0.50) {
               fValue <- "black"
               cat("!!!",xLevel,yLevel,zValue,mptcpMean,tcpMean,"\n")
            }
            else if(zValue < 0.80) {
               fValue <- "gray"
               cat("xxx",xLevel,yLevel,zValue,mptcpMean,tcpMean,"\n")
            }
            else {
               fValue <- getColor(100.0 * zValue, -200.0, 20000.0)
            }

zValue <- log(zValue)
if(zValue < 0) {
 cat('neg',zValue,"\n")
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
