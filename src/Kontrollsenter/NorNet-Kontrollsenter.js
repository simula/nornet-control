//
// NorNet Kontrollsenter JavaScript Functions
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


var displayLanguage = "NO";
var weekdayNames    = Array();
var monthNames      = Array();


// ###### Supported languages ###############################################
supportedDisplayLanguages = [ 'NO', 'UK', 'DE' ];


// ###### String translations ###############################################
weekdayNames['UK'] = new Array(7);
weekdayNames['UK'][0] = "Sunday";
weekdayNames['UK'][1] = "Monday";
weekdayNames['UK'][2] = "Tuesday";
weekdayNames['UK'][3] = "Wednesday";
weekdayNames['UK'][4] = "Thursday";
weekdayNames['UK'][5] = "Friday";
weekdayNames['UK'][6] = "Saturday";

monthNames['UK'] = new Array(12);
monthNames['UK'][0]  = "January";
monthNames['UK'][1]  = "February";
monthNames['UK'][2]  = "March";
monthNames['UK'][3]  = "April";
monthNames['UK'][4]  = "May";
monthNames['UK'][5]  = "June";
monthNames['UK'][6]  = "July";
monthNames['UK'][7]  = "August";
monthNames['UK'][8]  = "September";
monthNames['UK'][9]  = "October";
monthNames['UK'][10] = "November";
monthNames['UK'][11] = "December";

weekdayNames['DE'] = new Array(7);
weekdayNames['DE'][0] = "Sonntag";
weekdayNames['DE'][1] = "Montag";
weekdayNames['DE'][2] = "Dienstag";
weekdayNames['DE'][3] = "Mittwoch";
weekdayNames['DE'][4] = "Donnerstag";
weekdayNames['DE'][5] = "Freitag";
weekdayNames['DE'][6] = "Samstag";
monthNames['DE'] = new Array(12);
monthNames['DE'][0]  = "Januar";
monthNames['DE'][1]  = "Februar";
monthNames['DE'][2]  = "März";
monthNames['DE'][3]  = "April";
monthNames['DE'][4]  = "Mai";
monthNames['DE'][5]  = "Juni";
monthNames['DE'][6]  = "Juli";
monthNames['DE'][7]  = "August";
monthNames['DE'][8]  = "September";
monthNames['DE'][9]  = "Oktober";
monthNames['DE'][10] = "November";
monthNames['DE'][11] = "Dezember";

weekdayNames['NO'] = new Array(7);
weekdayNames['NO'][0] = "Søndag";
weekdayNames['NO'][1] = "Mandag";
weekdayNames['NO'][2] = "Tirsdag";
weekdayNames['NO'][3] = "Onsdag";
weekdayNames['NO'][4] = "Torsdag";
weekdayNames['NO'][5] = "Fredag";
weekdayNames['NO'][6] = "Lørdag";
monthNames['NO'] = new Array(12);
monthNames['NO'][0]  = "januar";
monthNames['NO'][1]  = "februar";
monthNames['NO'][2]  = "mars";
monthNames['NO'][3]  = "april";
monthNames['NO'][4]  = "mai";
monthNames['NO'][5]  = "juni";
monthNames['NO'][6]  = "july";
monthNames['NO'][7]  = "august";
monthNames['NO'][8]  = "september";
monthNames['NO'][9]  = "oktober";
monthNames['NO'][10] = "november";
monthNames['NO'][11] = "desember";

titleLabel = new Array()
titleLabel['UK'] = "Welcome to the NorNet Control Center at Simula Research Laboratory, Fornebu";
titleLabel['DE'] = "Willkommen im NorNet-Kontrollzentrum bei Simula Research Laboratory, Fornebu";
titleLabel['NO'] = "Velkommen til NorNet-Kontrollsenter på Simula Research Laboratory, Fornebu";

footerLabel = new Array()
footerLabel['UK'] = 'For further information on the NorNet Project, see <a href="http://www.nntb.no">http://www.nntb.no</a>!';
footerLabel['DE'] = 'Für weitere Informationen zum NorNet-Prosjekt siehe <a href="http://www.nntb.no">http://www.nntb.no</a>!';
footerLabel['NO'] = 'For mer informasjon om NorNet-prosjektet, se <a href="http://www.nntb.no">http://www.nntb.no</a>!';

updatingLabel = new Array()
updatingLabel['UK'] = "Updating ...";
updatingLabel['DE'] = "Aktualisiere ...";
updatingLabel['NO'] = "Oppdatering ...";

clockLabel = new Array()
clockLabel['UK'] = "Time";
clockLabel['DE'] = "Zeit";
clockLabel['NO'] = "Klokka";

problemsLabel = new Array()
problemsLabel['UK'] = "Problems:";
problemsLabel['DE'] = "Probleme:";
problemsLabel['NO'] = "Problemer:";

okayLabel = new Array()
okayLabel['UK'] = "Okay:";
okayLabel['DE'] = "In Ordnung:";
okayLabel['NO'] = "I orden:";

noProblemLabel = new Array()
noProblemLabel['UK'] = "&#128515; No problem! &#128515;";
noProblemLabel['DE'] = "&#128515; Kein Problem! &#128515;";
noProblemLabel['NO'] = "&#128515; Ingen problem! &#128515;";

sitesLabel = new Array()
sitesLabel['UK'] = "Sites";
sitesLabel['DE'] = "Standorte";
sitesLabel['NO'] = "Lokasjon";


// Dummy functions, to be replaced by dynamically-generated ones!
function makeMapContents() {}
function makeSidebarContents() {}


// ###### Update digital clock ##############################################
function updateClock()
{
  var currentTime    = new Date();
  var currentWeekday = currentTime.getDay();
  var currentDay     = currentTime.getDate();
  var currentMonth   = currentTime.getMonth();
  var currentYear    = currentTime.getFullYear();
  var currentHours   = currentTime.getHours();
  var currentMinutes = currentTime.getMinutes();
  var currentSeconds = currentTime.getSeconds();

  currentMinutes = (currentMinutes < 10 ? "0" : "") + currentMinutes;
  currentSeconds = (currentSeconds < 10 ? "0" : "") + currentSeconds;

  var currentTimeString = currentHours + ":" + currentMinutes + ":" + currentSeconds;
  var currentDateString = "";
  if( (displayLanguage != 'UK') ) {
     currentDateString = weekdayNames[displayLanguage][currentWeekday] + ", " +
                            currentDay + ".&nbsp;" + monthNames[displayLanguage][currentMonth] + "&nbsp;" + currentYear;

  }
  else {
     currentDateString = weekdayNames[displayLanguage][currentWeekday] + ", " +
                            monthNames[displayLanguage][currentMonth] + "&nbsp;" + currentDay + ",&nbsp;" + currentYear;

  }
  document.getElementById("date").innerHTML  = currentDateString;
  document.getElementById("clock").innerHTML = currentTimeString;
}


// ###### Update display contents ###########################################
function updateDisplay()
{
   document.getElementById("languages").innerHTML = "";
   for(i = 0;i < supportedDisplayLanguages.length; i++) {
      document.getElementById("languages").innerHTML = document.getElementById("languages").innerHTML +
         '<a href="javascript:" onclick="setLanguage(\'' +
         supportedDisplayLanguages[i] + '\');"><img id="languages.' +
         supportedDisplayLanguages[i] + '" class="' +
         ((supportedDisplayLanguages[i] == displayLanguage) ? "selected" : "normal") +
         '" src="Graphics/Flags/Flag-' +
         supportedDisplayLanguages[i] + '.png" alt="' +
         supportedDisplayLanguages[i] + '"" width="32" /></a> ';
   }

   document.getElementById("header.title").firstChild.nodeValue                 = titleLabel[displayLanguage];
   document.getElementById("footer.title").innerHTML                            = footerLabel[displayLanguage];
   // document.getElementById("sidebar.clock").firstChild.nodeValue                = clockLabel[displayLanguage];
   document.getElementById("sidebar.sites").firstChild.nodeValue                = sitesLabel[displayLanguage];
   document.getElementById("sidebar.sites.problems.title").firstChild.nodeValue = problemsLabel[displayLanguage];
   document.getElementById("sidebar.sites.okay.title").firstChild.nodeValue     = okayLabel[displayLanguage];
   if(document.getElementById("sites.noproblems") != null) {
      document.getElementById("sites.noproblems").innerHTML = noProblemLabel[displayLanguage];
   }
}


// ###### Set language ######################################################
function setLanguage(language)
{
   displayLanguage = language;
   updateDisplay();
   updateClock();
}


// ###### Auto-mode control #################################################
var autoMode = true;
function setAutoMode(on)
{
   autoMode = on;
   document.getElementById("automode").setAttribute("class", ((autoMode == true) ? "selected" : "normal"));
}


// ###### Initialize NorNet Kontrollsenter ##################################
var updateInterval = 30000;
function requestNorNetStatus()
{
   var xmlHttpRequest = new XMLHttpRequest();
   xmlHttpRequest.open("GET", "NorNet-Map.php", true);
   xmlHttpRequest.onreadystatechange = function() {
      if (xmlHttpRequest.readyState == 4) {
         if (xmlHttpRequest.status == 200) {
            try {
               // ====== Handle results =====================================
               eval(xmlHttpRequest.responseText);
               document.getElementById("footer.title").innerHTML = "OK!";
               updateDisplay();
               makeSidebarContents();
               makeMapContents();

               // ====== Auto-mode ==========================================
               if(autoMode == true) {
                  selectedMap = Math.round(Math.random() * (window.mapbaselayers.length));
                  window.map.setBaseLayer(window.mapbaselayers[selectedMap]);

                  showSelectedSite = Math.round(Math.random());
                  if((showSelectedSite == 1) && (window.mapContents.length > 0)) {
                     selectedSite = Math.round(Math.random() * (window.mapContents.length - 1));
                     zoomToSite(window.mapContents[selectedSite]);
                  }
                  else {
                     zoomToDefaultLocation();
                  }
               }
            }
            catch(errorMessage) {
               window.mapContents  = null;
               makeMapContents     = function(){};
               makeSidebarContents = function(){};
               updateDisplay();
               document.getElementById("footer.title").innerHTML = "ERROR: " + errorMessage;
            }
         }
         else {
            document.getElementById("footer.title").innerHTML = "BAD RESPONSE: " + xmlHttpRequest.status;
         }

         // ====== Schedule update ==========================================
         if(updateInterval < 5000) {
            updateInterval = 5000;   // The OpenLayers maps are quite computation-intensive ...
         }
         setTimeout("requestNorNetStatus()", updateInterval);
      }
   }

   document.getElementById("footer.title").innerHTML = updatingLabel[displayLanguage];
   xmlHttpRequest.send();
}


// ###### Initialize NorNet Kontrollsenter ##################################
function makeKontrollsenter()
{
   // ====== Handle arguments in URL ========================================
   var latitude   = 62.5;
   var longitude  = 5.0;
   var zoomLevel  = 5;
   var arguments = window.location.search.replace('?', '').split('&');
   for (var i = 0; i < arguments.length; i++) {
      option = arguments[i].split("=");
      if(option[0] == "latitude") {
         latitude = parseFloat(option[1]);
      }
      if(option[0] == "longitude") {
         longitude = parseFloat(option[1]);
      }
      else if(option[0] == "zoomlevel") {
         zoomLevel = Math.round(parseFloat(option[1]));
      }
      else if(option[0] == "update") {
         updateInterval = 1000 * Math.round(parseFloat(option[1]));
      }
      else if(option[0] == "auto") {
         autoMode = (Math.round(parseFloat(option[1])) != 0);
      }
   }

   var url = window.location.protocol + "//" + window.location.hostname;
   if(url.port >  "") {
      url = url + ":" + window.location.port;
   }
   url = url + "/" + window.location.pathname;

   // ====== Initialize everything ==========================================
   setAutoMode(autoMode);
   updateClock();
   setInterval('updateClock()', 1000);
   setLanguage('NO');
   makeMap(latitude, longitude, zoomLevel);

   // Now, get the NorNet status by using AJAX ...
   requestNorNetStatus();

//    // ====== Automatic page refresh =========================================
//    setTimeout("location.reload(false);", timeout * 1000);
//    document.getElementById("footer.title").innerHTML = 'URL='+url;
}

window.onload = makeKontrollsenter;
