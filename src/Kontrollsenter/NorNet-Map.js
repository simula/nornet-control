//
// NorNet Kontrollsenter
// Copyright (C) 2012-2016 by Thomas Dreibholz
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
         type: 'base', visible: false }),
//      new ol.layer.Tile({
//         title:   'OpenRailwayMap',
//         source:  new ol.source.OSM({
//            attributions: [ new ol.Attribution({ html: '<a href="http://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>, Style: <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA 2.0</a> <a href="http://www.openrailwaymap.org/">OpenRailwayMap</a> and OpenStreetMap' }) ],
//            url: 'http://{a-c}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png'
//         }),
//         type: 'base', visible: false }),

      new ol.layer.Tile({
         title:   'Thunderforest Outdoors',
         source:  new ol.source.OSM({
            attributions: [ new ol.Attribution({ html: '&copy; Gravitystorm Limited. Thunderforest is a project by <a href="http://www.gravitystorm.co.uk">Andy Allan</a>' }) ],
            url: 'https://{a-c}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png'
         }),
         type: 'base', visible: false }),
      new ol.layer.Tile({
         title:   'Thunderforest OpenCycleMap',
         source:  new ol.source.OSM({
            attributions: [ new ol.Attribution({ html: '&copy; Gravitystorm Limited. Thunderforest is a project by <a href="http://www.gravitystorm.co.uk">Andy Allan</a>' }) ],
            url: 'https://{a-c}.tile.thunderforest.com/cycle/{z}/{x}/{y}.png'
         }),
         type: 'base', visible: false }),
      new ol.layer.Tile({
         title:   'Thunderforest Transport',
         source:  new ol.source.OSM({
            attributions: [ new ol.Attribution({ html: '&copy; Gravitystorm Limited. Thunderforest is a project by <a href="http://www.gravitystorm.co.uk">Andy Allan</a>' }) ],
            url: 'https://{a-c}.tile.thunderforest.com/transport/{z}/{x}/{y}.png'
         }),
         type: 'base', visible: false }),
      new ol.layer.Tile({
         title:   'Thunderforest Transport Dark',
         source:  new ol.source.OSM({
            attributions: [ new ol.Attribution({ html: '&copy; Gravitystorm Limited. Thunderforest is a project by <a href="http://www.gravitystorm.co.uk">Andy Allan</a>' }) ],
            url: 'https://{a-c}.tile.thunderforest.com/transport-dark/{z}/{x}/{y}.png'
         }),
         type: 'base', visible: false }),
      new ol.layer.Tile({
         title:   'Thunderforest Landscape',
         source:  new ol.source.OSM({
            attributions: [ new ol.Attribution({ html: '&copy; Gravitystorm Limited. Thunderforest is a project by <a href="http://www.gravitystorm.co.uk">Andy Allan</a>' }) ],
            url: 'https://{a-c}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png'
         }),
         type: 'base', visible: false }),

      new ol.layer.Tile({
         title:   'Stamen Watercolor',
         source:  new ol.source.Stamen({ layer: 'watercolor' }),
         type:    'base', visible: false }),

      new ol.layer.Tile({
         title:   'Bing Aerial',
         source:  new ol.source.BingMaps({
            imagerySet: 'AerialWithLabels',
            key:        bingKey
         }),
         type: 'base', visible: false }),
      new ol.layer.Tile({
         title:   'Bing Road',
         source:  new ol.source.BingMaps({
            imagerySet: 'Road',
            key:        bingKey
         }),
         type: 'base', visible: false }),
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

   // ====== Create popup layer =============================================
   window.popup = new ol.Overlay({
                     element:     document.getElementById('popup'),
                     positioning: 'bottom-center',
                     stopEvent:   false,
                     autoPan:     true,
                     autoPanAnimation: {
                        duration: 250
                     }
                  });
   window.map.addOverlay(popup);

   // closer button
   var closer = document.getElementById('popup-closer');
   closer.onclick = function() {
      window.popup.setPosition(undefined);
      closer.blur();
      return false;
   };

   // display popup on click
   window.map.on('click', function(evt) {
      var feature = map.forEachFeatureAtPixel(evt.pixel,
         function(feature) {
           return feature;
         });
      if (feature) {
         if (feature.infoText != null) {
            document.getElementById('popup-content').innerHTML = feature.infoText;
            window.popup.setPosition(evt.coordinate);
         }
      }
      else {
         window.popup.setPosition(undefined);
      }
   });
                                             
   
   window.map.addControl(new ol.control.Zoom());
   window.map.addControl(new ol.control.ZoomSlider());
   window.map.addControl(new ol.control.ZoomToExtent());
   window.map.addControl(new ol.control.ScaleLine());
   window.map.addControl(new ol.control.Rotate());
   window.map.addControl(new ol.control.MousePosition({
      coordinateFormat: ol.coordinate.createStringXY(5),
      projection: 'EPSG:4326'
   }));
   window.map.addControl(new ol.control.OverviewMap( { view: new ol.View({ projection: 'EPSG:3857' }) } ));
   
   window.layerSwitcherControl = new ol.control.LayerSwitcher();
   window.map.addControl(window.layerSwitcherControl);
   
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
   markerFeature.infoText = infoText;   // This sets the popup content!

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
