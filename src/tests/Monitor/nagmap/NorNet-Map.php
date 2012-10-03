<?php
//
// NorNet Status Map
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
?>


// ###### Initialize NorNet map #############################################
function initializeNorNetMap()
{
   var myOptions = {
      zoom: 5,
      center: new google.maps.LatLng(62.5,5),
      mapTypeId: google.maps.MapTypeId.HYBRID
   };
   window.map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
}


<?php
include('NorNet-Status.php');
$status = getNorNetStatus();

// ###### Make contents of the map ##########################################
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


// ###### Make contents of the sidebar ######################################
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
