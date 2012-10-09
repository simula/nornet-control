//
// NorNet Map JavaScript Functions
// Copyright (C) 2012 by Thomas Dreibholz
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
// Contact: dreibh@simula.no
//


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
   window.maplayers     = new Array();   // All layers
   window.mapbaselayers = new Array();   // Only base layers

   // ====== Create Google map ==============================================
   window.googlemap1 = new OpenLayers.Layer.Google("Google Satellite", { type: google.maps.MapTypeId.HYBRID });
   window.maplayers.push(window.googlemap1);
   window.mapbaselayers.push(window.googlemap1);
   window.googlemap2 = new OpenLayers.Layer.Google("Google Terrain",   { type: google.maps.MapTypeId.TERRAIN });
   window.maplayers.push(window.googlemap2);
   window.mapbaselayers.push(window.googlemap2);

   // ====== Create OSM map (Mapnik tiles) ==================================
   window.mapnik    = new OpenLayers.Layer.OSM.Mapnik("Mapnik");
   window.mapnik.setOpacity(1.0);
   window.maplayers.push(window.mapnik);
   window.mapbaselayers.push(window.googlemap2);

   // window.wstations = new OpenLayers.Layer.Vector.OWMClusterStations("Stations");
   // window.maplayers.push(wstations);
   window.wcity = new OpenLayers.Layer.Vector.OWMWeather("Weather");
   window.maplayers.push(wcity);

   // ====== Create layers for markers and vectors ==========================
   window.mapvectors = new OpenLayers.Layer.Vector("Connections");
   window.maplayers.push(window.mapvectors);
   window.mapmarkers = new OpenLayers.Layer.Markers("Sites");
   window.maplayers.push(window.mapmarkers);

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
      layers:            window.maplayers,
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
                  12);
   document.getElementById("footer.title").innerHTML = '"' + site['name'] + '"';
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
