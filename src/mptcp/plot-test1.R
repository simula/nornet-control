library(scatterplot3d)
source("plotter.R")


# ###### Colourize output ###################################################
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



for(onlyNegativeResults in c(FALSE, TRUE)) {
   for(filterProtocol in c(4, 6)) {
      # outputFile <- "test1.pdf"
      outputFile <- sprintf("Results-IPv%s-%s.pdf", filterProtocol, onlyNegativeResults)

      if(onlyNegativeResults == TRUE) {
         labZ <- 4
      } else {
         labZ <- 6
      }

      data <- loadResults("passive.flow-ReceivedBytes.data.bz2")
      filter <- TRUE
      d <- subset(data, filter)


      xTitle <- "Source Endpoint"
      xSet   <- factor(d$FromProviderIndex * 256 + d$FromSiteIndex)
      yTitle <- "Destination Endpoint"
      ySet   <- factor(d$ToProviderIndex * 256 + d$ToSiteIndex)
      zTitle <- "MPTCP Gain in Log Scale [1]"


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
      xLevel <- 1
      for(xValue in levels(xSet)) {
         yLevel <- 1
         for(yValue in levels(ySet)) {
            filter <- (xSet == xValue) & (ySet == yValue) & (d$IPVersion == filterProtocol)
            mptcp <- subset(d, filter & (d$CMT == "mptcp"))
            tcp   <- subset(d, filter & (d$CMT == "off"))

            mptcpMean <- mean(mptcp$passive.flow.ReceivedBytes)
            tcpMean   <- mean(tcp$passive.flow.ReceivedBytes)
            zValue <- mptcpMean / tcpMean

            if(!is.na(zValue) && (zValue > 0.0)) {

               if(zValue < 0.80) {
                  fValue <- "gray"
                  info   <- "xxx"
                  if(zValue < 0.50) {
                     fValue <- "black"
                     info   <- "!!!"
                  }
                  cat(sep="", info, "\tx=",xLevel,"\ty=",yLevel,"\t",
                     "from=",mptcp$FromProviderIndex[1],"/",mptcp$FromSiteIndex[1], " -> ",
                     "to=",mptcp$ToProviderIndex[1],"/",mptcp$ToSiteIndex[1], "\t",
                     "\tz=",zValue,"\ttcp=",tcpMean,"\tmptcp=",mptcpMean,"\n")
               }
               else {
                  fValue <- getColor(100.0 * zValue, -200.0, 2000.0)
               }

               zLogValue <- log(zValue)


               if((onlyNegativeResults == FALSE) || (zValue < 0.97)) {
                  x <- append(x, xLevel)
                  y <- append(y, yLevel)
                  z <- append(z, zLogValue)
                  f <- append(f, fValue)
               }
            }

            yLevel <- yLevel + 1
         }
         xLevel <- xLevel + 1
      }


      x <- append(x, 0)
      y <- append(y, 0)
      z <- append(z, NA)
      f <- append(f, NA)

      x <- append(x, 27)
      y <- append(y, 27)
      z <- append(z, NA)
      f <- append(f, NA)

      pdf(outputFile, width=15, height=10, family="Helvetica", pointsize=22)
      scatterplot3d(x, y, z, highlight.3d=FALSE, color=f,
      xlab=xTitle, ylab=yTitle, zlab=zTitle,
      lab=c(14,14), lab.z=labZ,
      col.axis="blue", col.grid="lightblue", type="h",
      pch=16)
      dev.off()
   }
}
