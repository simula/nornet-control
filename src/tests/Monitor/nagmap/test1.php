<html>

<head>

<title>Velkommen til NorNet-Kontrollsenter på Simula, Fornebu</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="Author" content="Thomas Dreibholz" />
<meta name="Description" content="NorNet-Kontrollsenter" />
<meta name="Keywords" content="NorNet-Kontrollsenter, NorNet Project, NorNet Prosjekt, Simula Research Laboratory, Thomas Dreibholz" />
<meta name="Classification" content="Kontrollsenter" />
<link rel="stylesheet" href="stylesheet.css" type="text/css" />
<link rel="shortcut icon" href="graphics/icons/icon-uniessen.png" />
<script src="http://maps.google.com/maps/api/js?sensor=false" type="text/javascript"></script>
<script type="text/javascript">

var displayLanguage = "NO";

var weekdayNames = Array();
var monthNames   = Array();

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

clockLabel = new Array()
clockLabel['EN'] = "Time";
clockLabel['DE'] = "Zeit";
clockLabel['NO'] = "Klokka";

problemsLabel = new Array()
problemsLabel['EN'] = "Problems";
problemsLabel['DE'] = "Probleme";
problemsLabel['NO'] = "Problemer";

okayLabel = new Array()
okayLabel['EN'] = "Okay";
okayLabel['DE'] = "In Ordnung";
okayLabel['NO'] = "I orden";

sitesLabel = new Array()
sitesLabel['EN'] = "Sites";
sitesLabel['DE'] = "Standorte";
sitesLabel['NO'] = "Beliggenheter";


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


function makeDisplay()
{
//    makeSidebarContents()
   // document.getElementById("sidebar.clock").firstChild.nodeValue                = clockLabel[displayLanguage];
   document.getElementById("sidebar.sites").firstChild.nodeValue                = sitesLabel[displayLanguage];
   document.getElementById("sidebar.sites.problems.title").firstChild.nodeValue = problemsLabel[displayLanguage];
   document.getElementById("sidebar.sites.okay.title").firstChild.nodeValue     = okayLabel[displayLanguage];
   document.getElementById("header.title").firstChild.nodeValue                 = titleLabel[displayLanguage];
   updateClock();
   setInterval('updateClock()', 1000)
   makeMapContents();
}



function initialize() {
   var myOptions = {
      zoom: 5,
      center: new google.maps.LatLng(62.5,5),
      mapTypeId: google.maps.MapTypeId.HYBRID
   };
   window.map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
   makeDisplay();
}

window.onload=initialize;

<?php
   include('NorNet-Status.php');
   $status = getNorNetStatus();

   // ###### Make contents of the map #######################################
   echo "function makeMapContents() {\n";
   foreach ($status as $hostName => $hostEntry) {
      if (isset($status[$hostName][""]["location"])) {
         // ====== Create position for sites ================================
         echo '   // ====== ' . $hostName . ' ======' . "\n";
         echo '   window.' . $status[$hostName][""]["host_identifier"] . '_position = new google.maps.LatLng(' . $status[$hostName][""]["location"] . ');' . "\n";

         // ====== Create marker ============================================
         $site       = $hostName;
         $siteStatus = $status[$site][""]["last_hard_state"];
         $icon       = "http://www.google.com/mapfiles/marker_grey.png";
         if ($siteStatus == 0) {
            $icon = "http://www.google.com/mapfiles/marker_green.png";
         }
         elseif ($siteStatus == 1) {
            $icon = "http://www.google.com/mapfiles/marker_orange.png";
         }
         elseif ($siteStatus == 2) {
            $icon = "http://www.google.com/mapfiles/marker.png";
         }

         echo '   window.' . $status[$hostName][""]["host_identifier"] . '_marker   = new google.maps.Marker({'.
            "\n" . '      title:    "' . $hostName . '",'.
            "\n" . '      icon:     "' . $icon . '",'.
            "\n" . '      map:      window.map,'.
            "\n" . '      position: window.' . $status[$hostName][""]["host_identifier"] . '_position,'.
            "\n" . '      visible:  true,'.
            "\n" . '      zIndex:   1'.
            "\n" . '   });' . "\n";

         // ====== Create information window ================================
         if (!isset($h["parents"])) {
            $h["parents"] = Array();
         };
         $siteInfo = '<div class=\"bubble\"><b>'.$hostName."</b><br />xxxxx</div>";
         echo '   window.' . $status[$hostName][""]["host_identifier"] . '_information = new google.maps.InfoWindow({ content: "'. $siteInfo . '" });' . "\n";
         echo '   google.maps.event.addListener(' . $status[$hostName][""]["host_identifier"] . '_marker, "click", function() { ' .$status[$hostName][""]["host_identifier"]. '_information.open(map,' . $status[$hostName][""]["host_identifier"] . '_marker) } );' . "\n";
         echo "\n";
      }
   }
   echo "}\n\n";


   // ###### Make contents of the sidebar ###################################
   echo "function makeSidebarContents() {\n";
   $sitesContent = "";
   $problems = 0;
   $addedProblemsSection = false;
   foreach (array('critical', 'warning', 'unknown', 'ok') as $severity) {
      $categoryContent = "";
      foreach ($status as $hostName => $hostEntry) {
         if (isset($status[$hostName][""]["location"])) {
            $site       = $hostName;
            $siteStatus = $status[$hostName][""]["last_hard_state"];

            if( ($severity == "critical") &&
               ($siteStatus == 2) ) {
               $categoryContent = $categoryContent . '<li class="critical"><blink><strong>&#9760;</strong></blink>' . $site . '</li>';
               $problems++;
            }
            elseif( ($severity == "warning") &&
                  ($siteStatus == 1) ) {
               $categoryContent = $categoryContent . '<li class="warning">&#128544;' . $site . '</li>';
               $problems++;
            }
            elseif( ($severity == "unknown") &&
                  ($siteStatus > 2) ) {
               $categoryContent = $categoryContent . '<li class="unknown">&#128528;' . $site . '</li>';
            }
            elseif( ($severity == "ok") &&
                  ($siteStatus == 0) ) {
               $categoryContent = $categoryContent . '<li class="ok">&#128515;' . $site . '</li>';
               $problems++;
            }
         }
      }
      if ($categoryContent != "") {
         if ( ($severity == "critical") || ($severity == "warning") ) {
            if ($addedProblemsSection == false) {
               $sitesContent = $sitesContent . '<h3 id="sidebar.sites.problems.title">Problems</h3>';
               $addedProblemsSection = true;
            }
         }
         else if ($severity == 'ok') {
            $sitesContent = $sitesContent . '<h3 id="sidebar.sites.okay.title">Okay</h3>';
         }
         $sitesContent = $sitesContent . "<ul>" . $categoryContent . "</ul>";
      }
      elseif ( ($severity == "warning") && ($problems == 0) ) {
         $sitesContent = $sitesContent . '<h3 id="sites.noproblems">&#128515; Ingen problem! &#128515;</h3>';
      }

      if ($severity == "unknown") {
         echo "   document.getElementById(\"sidebar.sites.problems\").innerHTML = '" . $sitesContent . "';\n";
         $sitesContent = "";
      }
      else {
         echo "   document.getElementById(\"sidebar.sites.okay\").innerHTML = '" . $sitesContent . "';\n";
      }
   }

   echo "}\n\n";
?>

</script>

</head>

<body>

<div id="header" class="header">
 <h1 style="margin:0px; padding:0px;" id="header.title">&nbsp;</h1>
</div>

<div id="map_canvas" class="map" style="height: 100%;">
 <noscript>
  <h2>NorNet Map requires JavaScript!</h2>
 </noscript>
</div>

<div id="sidebar" class="sidebar">
 <h2 style="text-align: center;">
  <p class="center">
  <a href="javascript:" onclick="displayLanguage='NO'; makeDisplay();"><img src="graphics/flags/flag-norway.png" alt="Norsk" width="32" /></a>
  <a href="javascript:" onclick="displayLanguage='EN'; makeDisplay();"><img src="graphics/flags/flag-england.png" alt="English" width="32" /></a>
  <a href="javascript:" onclick="displayLanguage='DE'; makeDisplay();"><img src="graphics/flags/flag-germany.png" alt="Deutsch" width="32" /></a>
  </p>
 </h2>
 <hr />

<!--  <h2 id="sidebar.clock">Time</h2> -->
  <p class="center">
  <object data="station-clock.svg" type="image/svg+xml" class="clock">
   <param name="dial"               value="din 41091.1"/>
   <param name="hourHand"           value="siemens"/>
   <param name="minuteHand"         value="siemens"/>
   <param name="secondHand"         value="din 41071.2"/>
   <param name="minuteHandBehavior" value="stepping"/>
   <param name="secondHandBehavior" value="swinging"/>
   <param name="secondHandStopToGo" value="yes"/>
   <param name="secondHandStopTime" value="1.5"/>
   <param name="backgroundColor"    value="rgba(0,0,0,0)"/>
   <param name="dialColor"          value="rgb(40,40,40)"/>
   <param name="hourHandColor"      value="rgb(20,20,20)"/>
   <param name="minuteHandColor"    value="rgb(20,20,20)"/>
   <param name="secondHandColor"    value="rgb(160,50,40)"/>
   <param name="axisCoverColor"     value="rgb(20,20,20)"/>
   <param name="axisCoverRadius"    value="7"/>
   <param name="updateInterval"     value="50"/>
  </object>
  <br />
  <span id="clock" class="time">--:--:--</span><br />
  <span id="date" class="date">--</span>
  </p>
 <hr />

 <h2 id="sidebar.sites">Sites</h2>
  <span id="sidebar.sites.problems">Problems</span>
  <span id="sidebar.sites.okay">Okay</span>

</div>

<div id="footer" class="footer">
  For mer informasjon om NorNet-prosjektet, se <a href="http://www.nntb.no">http://www.nntb.no</a>!
</div>

</body>

</html>
