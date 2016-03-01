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
   window.maplayers     = new Array();   // All layers
   window.mapbaselayers = new Array();   // Only base layers

   // ====== Create layers for markers and vectors ==========================
//   window.mapmarkers = new ol.Layer.Markers("NorNet Sites");
//   window.maplayers.push(window.mapmarkers);
//   window.mapvectors = new ol.Layer.Vector("NorNet Connections");
//   window.maplayers.push(window.mapvectors);

   // ====== Create OSM map =================================================
   window.maplayers = [
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
      new ol.layer.Tile({
         title:   'OpenRailwayMap',
         source:  new ol.source.OSM({
            attributions: [ new ol.Attribution({ html: '<a href="http://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>, Style: <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA 2.0</a> <a href="http://www.openrailwaymap.org/">OpenRailwayMap</a> and OpenStreetMap' }) ],
            url: 'http://{a-c}.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png'
         }),
         type:    'base', visible: false }),
      new ol.layer.Tile({
         title:   'Stamen Watercolor',
         source:  new ol.source.Stamen({ layer: 'watercolor' }),
         type:    'base', visible: false }),
      new ol.layer.Tile({
         title:   'Stamen Terrain',
         source:  new ol.source.Stamen({ layer: 'terrain' }),
         type:    'base', visible: false })
   ]

   // ====== Create Google map ==============================================
//   window.googlemap1 = new OpenLayers.Layer.Google("Google Satellite", { type: google.maps.MapTypeId.HYBRID });
//   window.maplayers.push(window.googlemap1);
//   window.mapbaselayers.push(window.googlemap1);
//   window.googlemap2 = new OpenLayers.Layer.Google("Google Terrain",   { type: google.maps.MapTypeId.TERRAIN });
//   window.maplayers.push(window.googlemap2);
//   window.mapbaselayers.push(window.googlemap2);

   // ====== Create Bing map ================================================
   // FIXME: TEST ONLY! Needs proper API key!
//   var apiKey = "Agl-rpGco3Mo07n16sDpY4jsu35RAbvEwPAND7hi8-6JgIFVetQdhnZ4i_oSiNyd";
//   window.bingmap1 = new OpenLayers.Layer.Bing( { name: "Bing Road", key: apiKey, type: "Road" } );
//   window.maplayers.push(window.bingmap1);
//   window.mapbaselayers.push(window.bingmap1);
//   window.bingmap2 = new OpenLayers.Layer.Bing( { name: "Bing Aerial", key: apiKey, type: "AerialWithLabels" } );
//   window.maplayers.push(window.bingmap2);
//   window.mapbaselayers.push(window.bingmap2);

   // ====== OpenWeather overlay ============================================
   // FIXME: TEST ONLY! Needs proper APP ID! Example: http://openweathermap.org/current
//   var appID = "44db6a862fba0b067b1930da0d769e98";
//   window.wcity = new OpenLayers.Layer.Vector.OWMWeather("Weather", { 'appid' : appID } );
//   window.maplayers.push(wcity);

//   window.wstations = new OpenLayers.Layer.Vector.OWMStations("Stations");
//   window.wstations.setVisibility(false);
//   window.maplayers.push(wstations);


//   window.wclouds = new OpenLayers.Layer.XYZ("Clouds", "http://${s}.tile.openweathermap.org/map/clouds/${z}/${x}/${y}.png",
//                                             { isBaseLayer: false, sphericalMercator: true, opacity: 0.5 } );
//   window.wclouds.setVisibility(false);
//   window.maplayers.push(wclouds);
//
//   window.wpressure = new OpenLayers.Layer.XYZ("Pressure", "http://${s}.tile.openweathermap.org/map/pressure_cntr/${z}/${x}/${y}.png",
//                                               { isBaseLayer: false, sphericalMercator: true, opacity: 0.5 } );
//   window.wpressure.setVisibility(false);
//   window.maplayers.push(wpressure);
//
//   window.wwind = new OpenLayers.Layer.XYZ("Wind", "http://${s}.tile.openweathermap.org/map/wind/${z}/${x}/${y}.png",
//                                               { isBaseLayer: false, sphericalMercator: true, opacity: 0.5 } );
//   window.wwind.setVisibility(false);
//   window.maplayers.push(wwind);
//
//   window.wtemperature = new OpenLayers.Layer.XYZ("Temperature", "http://${s}.tile.openweathermap.org/map/temp/${z}/${x}/${y}.png",
//                                                    { isBaseLayer: false, sphericalMercator: true, opacity: 0.5 } );
//   window.wtemperature.setVisibility(false);
//   window.maplayers.push(wtemperature);
//
//   window.wrain = new OpenLayers.Layer.XYZ("Rain", "http://${s}.tile.openweathermap.org/map/rain/${z}/${x}/${y}.png",
//                                                    { isBaseLayer: false, sphericalMercator: true, opacity: 0.5 } );
//   window.wrain.setVisibility(false);
//   window.maplayers.push(wrain);
//
//   window.wsnow = new OpenLayers.Layer.XYZ("Snow", "http://${s}.tile.openweathermap.org/map/snow/${z}/${x}/${y}.png",
//                                                    { isBaseLayer: false, sphericalMercator: true, opacity: 0.5 } );
//   window.wsnow.setVisibility(false);
//   window.maplayers.push(wsnow);

   // ====== Create the map =================================================
   window.maplayers.reverse();
   window.map = new ol.Map({
      target:  'map_canvas',
//      view:    new ol.View({ //projection: 'EPSG:3857',
//                             center: ol.proj.transform([50, 5], 'EPSG:4326', 'EPSG:3857'),
//                             zoom: 5 }),
      layers:  new ol.layer.Group({ 'title': 'Base maps',
                                    layers:  window.maplayers
                                  }),

//      window.maplayers,
//      controls: [
//         new OpenLayers.Control.PanZoomBar(),
//         new ol.control.Zoom(),
//         new ol.control.ZoomSlider(),
//         new ol.control.ZoomToExtent(),
//         new ol.control.ScaleLine(),
//         new ol.control.Rotate(),
//         new OpenLayers.Control.Navigation(),
//         new ol.control.MousePosition(),
         //new ol.control.OverviewMap(),
//         new OpenLayers.Control.KeyboardDefaults(),
//         new OpenLayers.Control.LayerSwitcher( { 'ascending': false } )
//      ]
   });
   
   window.map.addControl(new ol.control.Zoom());
   window.map.addControl(new ol.control.ZoomSlider());
   window.map.addControl(new ol.control.ZoomToExtent());
   window.map.addControl(new ol.control.ScaleLine());
   window.map.addControl(new ol.control.Rotate());
   window.map.addControl(new ol.control.MousePosition());
   window.map.addControl(new ol.control.OverviewMap( { view: new ol.View({ projection: 'EPSG:3857' }) } ));

   window.map.addControl(new ol.control.LayerSwitcher({
      tipLabel: 'Légende' // Optional label for button
   }));
   
   window.default_latitude  = latitude;
   window.default_longitude = longitude;
   window.default_zoomlevel = zoomLevel;
   zoomToDefaultLocation();
}


// ###### Zoom to given location ############################################
function zoomToLocation(latitude, longitude, zoomLevel)
{
   window.map.setView(new ol.View({
//                         projection: 'EPSG:3857',
                         center:     ol.proj.transform([longitude, latitude], 'EPSG:4326', 'EPSG:3857'),
                         zoom:       zoomLevel}));
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
//   position = new OpenLayers.LonLat(longitude, latitude).transform(
//                 new OpenLayers.Projection("EPSG:4326"),
//                 window.map.getProjectionObject());
//   setVariable(positionVariable, position);
}


// ###### Remove marker #####################################################
function removeMarker(markerVariable)
{
   if (variableExists(markerVariable) && (getVariable(markerVariable) != null)) {
      var markerFeature = getVariable(markerVariable);
      window.mapmarkers.removeMarker(markerFeature.markerReference);
      // markerFeature.destroyMarker();
      markerFeature.destroy();
      setVariable(markerVariable, null);
   }
}


// ###### Create marker #####################################################
function makeMarker(markerVariable, title, icon, positionVariable, zIndex, infoText)
{
   removeMarker(markerVariable);

// !!!!!!!!!!!!!!!!!!!!!!!!!!!

   return;

   var markerFeature = new OpenLayers.Feature(window.mapmarkers, getVariable(positionVariable));
   markerFeature.closeBox              = true;
   markerFeature.popupClass            = OpenLayers.Class(OpenLayers.Popup.FramedCloud, { 'autoSize': true });
   markerFeature.data.popupContentHTML = infoText;
   markerFeature.data.overflow         = "hidden";
   markerFeature.data.icon             = new OpenLayers.Icon(icon,
                                                             new OpenLayers.Size(24,38), null,
                                                             function(size) {
                                                                return new OpenLayers.Pixel(-(size.w/2), -size.h);
                                                             });
   markerFeature.markerReference       = markerFeature.createMarker();
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
   markerFeature.markerReference.events.register("mousedown", markerFeature, markerClick);
   window.mapmarkers.addMarker(markerFeature.markerReference);

   setVariable(markerVariable, markerFeature);
}


// ###### Remove connection #################################################
function removeConnection(connectionVariable)
{
   if (variableExists(connectionVariable) && (getVariable(connectionVariable) != null)) {
      var connection = getVariable(connectionVariable);
//      window.mapvectors.removeFeatures([connection], true);
      connection.destroy();
      setVariable(connectionVariable, null);
   }
}

// ###### Create connection #################################################
function makeConnection(connectionVariable, points, color, thickness, dashStyle, zIndex)
{
   removeConnection(connectionVariable);
   var linePoints = [];
//   for(i = 0;i < points.length; i++) {
//      linePoints[i] = new OpenLayers.Geometry.Point(points[i].lon, points[i].lat);
//   }
//   var lineString = new OpenLayers.Geometry.LineString(linePoints);
//   var connection = new OpenLayers.Feature.Vector(lineString, null, {
//         strokeColor:     color,
//         strokeOpacity:   0.9,
//         strokeWidth:     thickness,
//         strokeDashstyle: dashStyle,
//         graphicZIndex:   zIndex
//      });
//   window.mapvectors.addFeatures([connection]);
//
//   setVariable(connectionVariable, connection);
}
