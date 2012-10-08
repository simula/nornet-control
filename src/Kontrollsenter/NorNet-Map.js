// ###### Check existence of variable given by its name #####################
function variableExists(variable)
{
   return(eval("typeof(" + variable + ")") != "undefined");
}


// ###### Get content of variable given by its name #########################
function getVariable(variable)
{
   var value;
   eval("value=(" + variable + ");");
   return(value);
}


// ###### Set content of variable given by its name #########################
function setVariable(variable, value)
{
   eval(variable + "=value;");
}


// ###### Initialize NorNet map #############################################
function makeMap(latitude, longitude, zoomLevel)
{
   // ====== Create Google map ==============================================
   window.googlemap = new OpenLayers.Layer.Google("Google", { type: google.maps.MapTypeId.HYBRID });

   // ====== Create OSM map (Mapnik tiles) ==================================
   window.mapnik    = new OpenLayers.Layer.OSM.Mapnik("Mapnik");
   window.mapnik.setOpacity(1.0);

   // ====== Create layers for markers and vectors ==========================
   window.mapmarkers = new OpenLayers.Layer.Markers("Sites");
   window.mapvectors = new OpenLayers.Layer.Vector("Connections");

   // ====== Caching ========================================================
   window.mapcache_read  = new OpenLayers.Control.CacheRead();
   window.mapcache_read.activate();
   window.mapcache_write = new OpenLayers.Control.CacheWrite();
   window.mapcache_write.activate();

   // ====== Create the map =================================================
   window.map = new OpenLayers.Map({
      div:               "map_canvas",
      units:             "m",
      displayProjection: new OpenLayers.Projection("EPSG:4326"),
      layers: [
         window.googlemap,
         window.mapnik,
         window.mapvectors,
         window.mapmarkers
      ],
      controls: [
         window.mapcache_read,
         window.mapcache_write,
         new OpenLayers.Control.Navigation(),
         new OpenLayers.Control.PanZoomBar(),
         new OpenLayers.Control.LayerSwitcher({'ascending':false}),
         new OpenLayers.Control.Permalink(),
         new OpenLayers.Control.ScaleLine(),
         new OpenLayers.Control.Permalink('permalink'),
         new OpenLayers.Control.MousePosition(),
         new OpenLayers.Control.OverviewMap(),
         new OpenLayers.Control.KeyboardDefaults()
      ]
   });
   window.default_latitude  = latitude;
   window.default_longitude = longitude;
   window.default_zoomlevel = zoomLevel;
   zoomToDefaultLocation();
}


// ###### Zoom to given location ############################################
function zoomToLocation(latitude, longitude, zoomLevel)
{
   window.map.setCenter(new OpenLayers.LonLat(longitude, latitude).transform(
                           new OpenLayers.Projection("EPSG:4326"), window.map.getProjectionObject()),
                        zoomLevel);
}

// ###### Zoom to default location ##########################################
function zoomToDefaultLocation()
{
   zoomToLocation(window.default_latitude, window.default_longitude, window.default_zoomlevel);
}


// ###### Zoom to site ######################################################
function zoomToSite(site)
{
   zoomToLocation(site['latitude'],
                  site['longitude'],
                  11);
   document.getElementById("footer.title").innerHTML = site['name'];
}


// ###### Remove position ###################################################
function removePosition(positionVariable)
{
   setVariable(positionVariable, null);
}


// ###### Create position ###################################################
function makePosition(positionVariable, latitude, longitude)
{
   removePosition(positionVariable);
   position = new OpenLayers.LonLat(longitude, latitude).transform(
                 new OpenLayers.Projection("EPSG:4326"), window.map.getProjectionObject());
   setVariable(positionVariable, position);
}


// ###### Remove marker #####################################################
function removeMarker(markerVariable)
{
   if (variableExists(markerVariable) && (getVariable(markerVariable) != null)) {
      var marker = getVariable(markerVariable);
      marker.featureReference.destroy();   // Remove the Feature
      window.mapmarkers.removeMarker(marker);
      setVariable(markerVariable, null);
   }
}


// ###### Create marker #####################################################
function makeMarker(markerVariable, title, icon, positionVariable, zIndex, infoText)
{
   removeMarker(markerVariable);

   var markerFeature = new OpenLayers.Feature(window.mapmarkers, getVariable(positionVariable));
   markerFeature.closeBox              = true;
   markerFeature.popupClass            =  OpenLayers.Class(OpenLayers.Popup.FramedCloud, { 'autoSize': true });
   markerFeature.data.popupContentHTML = infoText;
   markerFeature.data.overflow         = "auto";
   markerFeature.data.icon             = new OpenLayers.Icon(icon);

   var marker      = markerFeature.createMarker();
   var markerClick = function (event) {
      if (this.popup == null) {
         this.popup = this.createPopup(this.closeBox);
         map.addPopup(this.popup);
         this.popup.show();
      } else {
         this.popup.toggle();
      }
      currentPopup = this.popup;
      OpenLayers.Event.stop(event);
   };
   marker.events.register("mousedown", markerFeature, markerClick);
   marker.featureReference = markerFeature;   // Store reference to Feature for later disposal.
   window.mapmarkers.addMarker(marker);

   setVariable(markerVariable, marker);
}


// ###### Remove connection #################################################
function removeConnection(connectionVariable)
{
   if (variableExists(connectionVariable) && (getVariable(connectionVariable) != null)) {
      var connection = getVariable(connectionVariable);
      window.mapvectors.removeFeatures([connection], true);
      setVariable(connectionVariable, null);
   }
}

// ###### Create connection #################################################
function makeConnection(connectionVariable, points, color, thickness, zIndex)
{
   removeConnection(connectionVariable);
   var linePoints = [];
   for(i = 0;i < points.length; i++) {
      linePoints[i] = new OpenLayers.Geometry.Point(points[i].lon, points[i].lat);
   }
   var lineString = new OpenLayers.Geometry.LineString(linePoints);
   var connection = new OpenLayers.Feature.Vector(lineString, null, {
         strokeColor:   color,
         strokeOpacity: 0.9,
         strokeWidth:   thickness
      });
   window.mapvectors.addFeatures([connection]);

   setVariable(connectionVariable, connection);
}
