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


// ###### String translations ###############################################
weekdayNames['EN'] = new Array(7);
weekdayNames['EN'][0] = "Sunday";
weekdayNames['EN'][1] = "Monday";
weekdayNames['EN'][2] = "Tuesday";
weekdayNames['EN'][3] = "Wednesday";
weekdayNames['EN'][4] = "Thursday";
weekdayNames['EN'][5] = "Friday";
weekdayNames['EN'][6] = "Saturday";

monthNames['EN'] = new Array(12);
monthNames['EN'][0]  = "January";
monthNames['EN'][1]  = "February";
monthNames['EN'][2]  = "March";
monthNames['EN'][3]  = "April";
monthNames['EN'][4]  = "May";
monthNames['EN'][5]  = "June";
monthNames['EN'][6]  = "July";
monthNames['EN'][7]  = "August";
monthNames['EN'][8]  = "September";
monthNames['EN'][9]  = "October";
monthNames['EN'][10] = "November";
monthNames['EN'][11] = "December";

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
titleLabel['EN'] = "Welcome to the NorNet Control Center at Simula, Fornebu";
titleLabel['DE'] = "Willkommen im NorNet-Kontrollzentrum bei Simula, Fornebu";
titleLabel['NO'] = "Velkommen til NorNet-Kontrollsenter på Simula, Fornebu";

footerLabel = new Array()
footerLabel['EN'] = 'For further information on the NorNet Project, see <a href="http://www.nntb.no">http://www.nntb.no</a>!';
footerLabel['DE'] = 'Für weitere Informationen zum NorNet-Prosjekt siehe <a href="http://www.nntb.no">http://www.nntb.no</a>!';
footerLabel['NO'] = 'For mer informasjon om NorNet-prosjektet, se <a href="http://www.nntb.no">http://www.nntb.no</a>!';


clockLabel = new Array()
clockLabel['EN'] = "Time";
clockLabel['DE'] = "Zeit";
clockLabel['NO'] = "Klokka";

problemsLabel = new Array()
problemsLabel['EN'] = "Problems:";
problemsLabel['DE'] = "Probleme:";
problemsLabel['NO'] = "Problemer:";

okayLabel = new Array()
okayLabel['EN'] = "Okay:";
okayLabel['DE'] = "In Ordnung:";
okayLabel['NO'] = "I orden:";

noProblemLabel = new Array()
noProblemLabel['EN'] = "&#128515; No problem! &#128515;";
noProblemLabel['DE'] = "&#128515; Kein Problem! &#128515;";
noProblemLabel['NO'] = "&#128515; Ingen problem! &#128515;";

sitesLabel = new Array()
sitesLabel['EN'] = "Sites";
sitesLabel['DE'] = "Standorte";
sitesLabel['NO'] = "Beliggenheter";


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
  if( (displayLanguage == "NO") || (displayLanguage == "DE")) {
     currentDateString = weekdayNames[displayLanguage][currentWeekday] + ", " +
                            currentDay + ". " + monthNames[displayLanguage][currentMonth] + " " + currentYear;

  }
  else {
     currentDateString = weekdayNames[displayLanguage][currentWeekday] + ", " +
                            monthNames[displayLanguage][currentMonth] + " " + currentDay + ", " + currentYear;

  }
  document.getElementById("date").firstChild.nodeValue  = currentDateString;
  document.getElementById("clock").firstChild.nodeValue = currentTimeString;
}


// ###### Update display contents ###########################################
function updateDisplay()
{
   // document.getElementById("sidebar.clock").firstChild.nodeValue                = clockLabel[displayLanguage];
   document.getElementById("sidebar.sites").firstChild.nodeValue                = sitesLabel[displayLanguage];
   document.getElementById("sidebar.sites.problems.title").firstChild.nodeValue = problemsLabel[displayLanguage];
   document.getElementById("sidebar.sites.okay.title").firstChild.nodeValue     = okayLabel[displayLanguage];
   if(document.getElementById("sidebar.sites.noproblems") != null) {
      document.getElementById("sidebar.sites.okay.title").firstChild.nodeValue = noProblemLabel[displayLanguage];
   }
   document.getElementById("header.title").firstChild.nodeValue                 = titleLabel[displayLanguage];
   document.getElementById("footer.title").innerHTML                            = footerLabel[displayLanguage];

   updateClock();
   setInterval('updateClock()', 1000)
   makeMapContents();
   makeSidebarContents()
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
   }

   // ====== Initialize everything ==========================================
   initializeNorNetMap(latitude, longitude, zoomLevel);
   updateDisplay();
}

window.onload=makeKontrollsenter;
