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
function initializeNorNetMap(latitude, longitude, zoomLevel)
{
   var myOptions = {
      zoom:   zoomLevel,
      center: new google.maps.LatLng(latitude, longitude),
      mapTypeId: google.maps.MapTypeId.HYBRID
   };
   window.map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
}


<?php
include('NorNet-Status.php');
$status = getNorNetStatus();

// ###### Make contents of the map ##########################################
echo "function makeMapContents() {\n";

// ====== Set up the sites ==================================================
foreach ($status as $hostName => $hostEntry) {
   if (isset($status[$hostName][""]["location"])) {
      // ====== Create position for sites ===================================
      echo '   // ====== ' . $hostName . ' ======' . "\n";
      echo '   window.' . $status[$hostName][""]["host_identifier"] . '_position = new google.maps.LatLng(' . $status[$hostName][""]["location"] . ');' . "\n";

      // ====== Create marker ===============================================
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

      // ====== Create information window ===================================
      if (!isset($h["parents"])) {
         $h["parents"] = Array();
      };
      $siteInfo = '<div class=\"bubble\"><b>'.$hostName."</b><br />xxxxx</div>";
      echo '   window.' . $status[$hostName][""]["host_identifier"] . '_information = new google.maps.InfoWindow({ content: "'. $siteInfo . '" });' . "\n";
      echo '   google.maps.event.addListener(' . $status[$hostName][""]["host_identifier"] . '_marker, "click", function() { ' .$status[$hostName][""]["host_identifier"]. '_information.open(map,' . $status[$hostName][""]["host_identifier"] . '_marker) } );' . "\n";
      echo "\n";
   }
}

// ====== Set up the links ==================================================
foreach ($status as $hostName => $hostEntry) {
   foreach ($hostEntry as $serviceName => $serviceEntry) {
      if ($serviceName != "") {   // A real service!
         if ( (isset($status[$hostName][$serviceName]["tunnel_local_host_name"])) &&
              (isset($status[$hostName][$serviceName]["tunnel_remote_host_name"])) ) {
            $tunnelState    = $status[$hostName][$serviceName]['last_hard_state'];
            $localHostName  = $status[$hostName][$serviceName]['tunnel_local_host_name'];
            $remoteHostName = $status[$hostName][$serviceName]['tunnel_remote_host_name'];

            $localIdentifer  = $status[$hostName][$serviceName]['tunnel_local_identifier'];
            $remoteIdentifer = $status[$hostName][$serviceName]['tunnel_remote_identifier'];

            $state = $status[$hostName][$serviceName]['last_hard_state'];

            if( ($state == 1) || ($state == 2) ||
                (isset($status[$hostName][""]['is_central_site'])) ) {

               $zIndex       = 10;
               $strokeWeight = 5;
               switch($state) {
                  case 0:
                     $linkColor = "#00ff00";
                   break;
                  case 1:
                     $linkColor = "yellow";
                     $zIndex    = 15;
                   break;
                  case 2:
                     $linkColor    = "red";
                     $strokeWeight = 10;
                     $zIndex       = 20;
                   break;
                  default:
                     $linkColor = "grey";
                   break;
               }

               echo "   // ====== Tunnel ".$localHostName." to ".$remoteHostName." S=".$tunnelState." ======\n";
               echo '   window.' . $localIdentifer . '_to_' . $remoteIdentifer . ' = new google.maps.Polyline({' . "\n" .
                  '     path: [window.' . $localIdentifer . '_position, window.' . $remoteIdentifer . '_position],' . "\n" .
                  '     zIndex:        ' . $zIndex . ',' . "\n" .
                  '     strokeColor:   "' . $linkColor . '",' . "\n" .
                  '     strokeOpacity: 0.9,' . "\n" .
                  '     strokeWeight:  ' . $strokeWeight . '});' . "\n";
               echo '   window.' . $localIdentifer . '_to_' . $remoteIdentifer . '.setMap(window.map);' . "\n\n";
             }
         }
      }
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
            $categoryContent = $categoryContent . '<li class="okay">&#128515;' . $site . '</li>';
         }
      }
   }
   if ($categoryContent != "") {
      if ( ($severity == "critical") || ($severity == "warning") ) {
         $addedProblemsSection = true;
      }
      $sitesContent = $sitesContent . "<ul>" . $categoryContent . "</ul>";
   }
   elseif ( ($severity == "warning") && ($problems == 0) ) {
      $sitesContent = $sitesContent . '<p class="allsitesokay" id="sites.noproblems">xxx</p>';
   }

   if ($severity == "unknown") {
      echo "   document.getElementById(\"sidebar.sites.problems\").innerHTML = '" . $sitesContent . "';\n";
      $sitesContent = "";
   }
   else {
      echo "   document.getElementById(\"sidebar.sites.okay\").innerHTML = '" . $sitesContent . "';\n";
   }
}
if($problems == 0) {
   echo "   document.getElementById(\"sites.noproblems\").innerHTML = noProblemLabel[displayLanguage];\n";
}

echo "}\n\n";
?>
