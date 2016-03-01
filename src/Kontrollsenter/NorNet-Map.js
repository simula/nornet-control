//
// NorNet Map JavaScript Functions
// Copyright (C) 2012-2015 by Thomas Dreibholz
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
   // ====== Create layers for markers and vectors ==========================
   window.sitesSource = new ol.source.Vector();
   window.sitesVector = new ol.layer.Vector({
      title:   'NorNet Sites',
      visible: true,
      source:  window.sitesSource
   });

   window.connectionsSource = new ol.source.Vector();
   window.connectionsVector = new ol.layer.Vector({
      title:   'NorNet Connections',
      visible: true,
      source:  window.connectionsSource
   });

   // ====== Map settings ===================================================
   // FIXME: TEST ONLY! Needs proper API key!
   bingKey = 'AkGbxXx6tDWf1swIhPJyoAVp06H0s0gDTYslNWWHZ6RoPqMpB9ld5FY1WutX8UoF';

   // ====== Create map layers ==============================================
   window.mapLayers = [
      new ol.layer.Tile({
         title:   'OpenStreetMap',
         source:  new ol.source.OSM(),
         type:    'base', visible: true }),
      new ol.layer.Tile({
         title:   'OpenCycleMap',
         source:  new ol.source.OSM({
            attributions: [ new ol.Attribution({ html: '<a href="http://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>, Style: <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA 2.0</a> <a href="http://www.opencyclemap.org/">OpenCycleMap</a> and OpenStreetMap' }) ],
            url: 'http://{a-c}.tile.opencyclemap.org/cycle/{z}/{x}/{y}.png'
         }),
         type:    'base', visible: false }),
//      new ol.layer.Tile({
//         title:   'OpenRailwayMap',
//         source:  new ol.source.OSM({
//            attributions: [ new ol.Attribution({ html: '<a href="http://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>, Style: <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA 2.0</a> <a href="http://www.openrailwaymap.org/">OpenRailwayMap</a> and OpenStreetMap' }) ],
//            url: 'http://{a-c}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png'
//         }),
//         type:    'base', visible: false }),

      new ol.layer.Tile({
         title:   'Stamen Watercolor',
         source:  new ol.source.Stamen({ layer: 'watercolor' }),
         type:    'base', visible: false }),
//      new ol.layer.Tile({
//         title:   'Stamen Terrain',
//         source:  new ol.source.Stamen({ layer: 'terrain' }),
//         type:    'base', visible: false }),
         
      new ol.layer.Tile({
         title:   'Bing Aerial',
         source:  new ol.source.BingMaps({
            imagerySet: 'AerialWithLabels',
            key:        bingKey
         }),
         type:   'base', visible: false }),
      new ol.layer.Tile({
         title:   'Bing Road',
         source:  new ol.source.BingMaps({
            imagerySet: 'Road',
            key:        bingKey
         }),
         type:   'base', visible: false }),
   ]

   // ====== Create overlay layers ==========================================
   window.overlayLayers = [
      window.sitesVector,
      window.connectionsVector,
      new ol.layer.Tile({
         title:   'Temperature',
         source:  new ol.source.XYZ({ url: 'http://{a-c}.tile.openweathermap.org/map/temp/{z}/{x}/{y}.png' }), opacity: 0.5, visible: false }),
      new ol.layer.Tile({
         title:   'Pressure',
         source:  new ol.source.XYZ({ url: 'http://{a-c}.tile.openweathermap.org/map/pressure_cntr/{z}/{x}/{y}.png' }), opacity: 0.5, visible: false }),
      new ol.layer.Tile({
         title:   'Clouds',
         source:  new ol.source.XYZ({ url: 'http://{a-c}.tile.openweathermap.org/map/clouds/{z}/{x}/{y}.png' }), opacity: 0.5, visible: false }),
      new ol.layer.Tile({
         title:   'Snow',
         source:  new ol.source.XYZ({ url: 'http://{a-c}.tile.openweathermap.org/map/snow/{z}/{x}/{y}.png' }), opacity: 0.5, visible: false }),
      new ol.layer.Tile({
         title:   'Rain',
         source:  new ol.source.XYZ({ url: 'http://{a-c}.tile.openweathermap.org/map/rain/{z}/{x}/{y}.png' }), opacity: 0.5, visible: false }),
      new ol.layer.Tile({
         title:   'Wind',
         source:  new ol.source.XYZ({ url: 'http://{a-c}.tile.openweathermap.org/map/wind/{z}/{x}/{y}.png' }), opacity: 0.5, visible: false }),
   ]

   // ====== Create the map =================================================
   window.mapLayers.reverse();
   window.overlayLayers.reverse();
   window.map = new ol.Map({
      target:  'map_canvas',
      layers:  [ new ol.layer.Group({ title:  'Base maps',
                                      layers: window.mapLayers }),
                 new ol.layer.Group({ title:  'Overlays',
                                      layers: window.overlayLayers  }) ]
   });
   
   window.map.addControl(new ol.control.Zoom());
   window.map.addControl(new ol.control.ZoomSlider());
   window.map.addControl(new ol.control.ZoomToExtent());
   window.map.addControl(new ol.control.ScaleLine());
   window.map.addControl(new ol.control.Rotate());
   window.map.addControl(new ol.control.MousePosition());
   window.map.addControl(new ol.control.OverviewMap( { view: new ol.View({ projection: 'EPSG:3857' }) } ));
   window.map.addControl(new ol.control.LayerSwitcher());
   
   window.default_latitude  = latitude;
   window.default_longitude = longitude;
   window.default_zoomlevel = zoomLevel;
   zoomToDefaultLocation();
}


// ###### Zoom to given location ############################################
function zoomToLocation(latitude, longitude, zoomLevel)
{
   window.map.setView(new ol.View({
                         center: ol.proj.transform([longitude, latitude], 'EPSG:4326', 'EPSG:3857'),
                         zoom:   zoomLevel}));
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

   var label = ""
   if(site['country_code'] != "") {
      label = label + '<img class="footerflag" src="/Artwork/Graphics/Flags/Flag-' + site['country_code'] + '.svg" alt="" />&nbsp;';
   }
   label = label + site['name'];
   if(site['city'] != "") {
      label = label + ", " + site['city'];
   }
   if(site['province'] != "") {
      label = label + ", " + site['province'];
   }
   if(site['country'] != "") {
      if( (site['city'] != "") || (site['province'] != "") ) {
         label = label + '/';
      }
      else {
         label = label + ', ';
      }
      label = label + site['country'];
   }
   if(site['province'] != "") {
      label = label + '&nbsp;<img class="footerflag" src="/Artwork/Graphics/Flags/' + site['country_code'] + '-' + site['province'] + '.svg" alt="" />';
   }
   document.getElementById("footer.title").innerHTML = label;
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
   position = new ol.geom.Point(ol.proj.transform([longitude, latitude], 'EPSG:4326', 'EPSG:3857'));
   setVariable(positionVariable, position);
}


// ###### Remove marker #####################################################
function removeMarker(markerVariable)
{
   if (variableExists(markerVariable) && (getVariable(markerVariable) != null)) {
      var markerFeature = getVariable(markerVariable);
      window.sitesSource.removeFeature(markerFeature);
      setVariable(markerVariable, null);
   }
}


// ###### Create marker #####################################################
function makeMarker(markerVariable, title, icon, positionVariable, zIndex, infoText)
{
   removeMarker(markerVariable);

   var markerFeature = new ol.Feature({
      geometry: getVariable(positionVariable),
      name:     title
   });
   markerFeature.setStyle(new ol.style.Style({
      image: new ol.style.Icon({
         anchor:       [0.5, 1],
         anchorXUnits: 'fraction',
         anchorYUnits: 'fraction',
         src:           icon
      })
   }));
      
//   var markerFeature = new ol.Feature(window.mapmarkers, getVariable(positionVariable));
//   markerFeature.closeBox              = true;
//   markerFeature.popupClass            = ol.Class(ol.Popup.FramedCloud, { 'autoSize': true });
//   markerFeature.data.popupContentHTML = infoText;
//   markerFeature.data.overflow         = "hidden";
//   markerFeature.data.icon             = new ol.Icon(icon,
//                                                             new ol.Size(24,38), null,
//                                                             function(size) {
//                                                                return new ol.Pixel(-(size.w/2), -size.h);
//                                                             });

//   markerFeature.markerReference       = markerFeature.createMarker();
//   var markerClick = function (event) {
//      if (this.popup == null) {
//         this.popup = this.createPopup(this.closeBox);
//         map.addPopup(this.popup);
//         this.popup.show();
//      } else {
//         this.popup.toggle();
//      }
//      currentPopup = this.popup;
//      OpenLayers.Event.stop(event);
//   };
//   markerFeature.markerReference.events.register("mousedown", markerFeature, markerClick);

   window.sitesSource.addFeature(markerFeature);
   setVariable(markerVariable, markerFeature);
}


// ###### Remove connection #################################################
function removeConnection(connectionVariable)
{
   if (variableExists(connectionVariable) && (getVariable(connectionVariable) != null)) {
      var connectionFeature = getVariable(connectionVariable);
      window.connectionsSource.removeFeature(connectionFeature);
      setVariable(connectionVariable, null);
   }
}

// ###### Create connection #################################################
function makeConnection(connectionVariable, points, color, thickness, dashStyle, zIndex)
{
   removeConnection(connectionVariable);
   var linePoints = []; 
   for(i = 0;i < points.length; i++) {
      linePoints[i] = points[i].getCoordinates()
   }   

   var connectionFeature = new ol.Feature({
      geometry: new ol.geom.LineString(linePoints)
   });
   connectionFeature.setStyle(new ol.style.Style({
      stroke : new ol.style.Stroke({
         color: color,
         width: thickness
      }),
      zIndex : zIndex
   }));

   window.connectionsSource.addFeature(connectionFeature); 
   setVariable(connectionVariable, connectionFeature);
}
