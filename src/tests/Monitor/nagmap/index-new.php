<?php
$page = $_SERVER['PHP_SELF'];
$sec = "300";
header("Refresh: $sec; url=$page");
$nagmap_version = '1.0';
include('./config.php');
// include('./call.php');
?>
<html>
  <head>
    <link rel="shortcut icon" href="favicon.ico" />
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
	<link rel=StyleSheet href="style.css" type="text/css" media=screen>
    <title>NorNet Kontrollsenter på Simula, Fornebu</title>
    <script src="http://maps.google.com/maps/api/js?sensor=false" type="text/javascript"></script>


<?php
   echo '<script type="text/javascript">' . "\n";

   include('marker.php');
   $status = nagmap_status();


   // ###### Make contents of the map #######################################
   echo "function makeMapContents() {\n";
   foreach ($hosts as $h) {
      if ((isset($h["latlng"])) and (isset($h["host_name"]))) {
         // ====== Create position for sites ================================
         echo '   // ====== ' . $h["nagios_host_name"] . ' ======' . "\n";
         echo '   window.' . $h["host_name"] . '_position = new google.maps.LatLng(' . $h["latlng"] . ');' . "\n";

         // ====== Create marker ============================================
         $site       = $h["nagios_host_name"];
         $siteStatus = $status[$site]["hoststatus"]["last_hard_state"];
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

         echo '   window.' . $h["host_name"] . '_marker   = new google.maps.Marker({'.
            "\n" . '      title:    "' . $h["nagios_host_name"] . '",'.
            "\n" . '      icon:     "' . $icon . '",'.
            "\n" . '      map:      window.map,'.
            "\n" . '      position: window.' . $h["host_name"] . '_position,'.
            "\n" . '      visible:  true,'.
            "\n" . '      zIndex:   1'.
            "\n" . '   });' . "\n";

         // ====== Create information window ================================
         if (!isset($h["parents"])) {
            $h["parents"] = Array();
         };
         $siteInfo = '<div class=\"bubble\"><b>'.$h["nagios_host_name"]."</b><br>Type: ".$h["use"].'</div>';
         echo '   window.' . $h["host_name"] . '_information = new google.maps.InfoWindow({ content: "'. $siteInfo . '" });' . "\n";
         echo '   google.maps.event.addListener(' . $h["host_name"] . '_marker, "click", function() { ' .$h["host_name"]. '_information.open(map,' . $h["host_name"] . '_marker) } );' . "\n";
         echo "\n";

//     if (!isset($h["parents"])) { $h["parents"] = Array(); };
//     $info = '<div class=\"bubble\"><b>'.$h["nagios_host_name"]."</b><br>Type: ".$h["use"]
//          .'<br>Address:'.$h["address"]
//          .'<br>Number of parents:'.count($h["parents"]).','
//          .'<br>Host status: '.$s[$h["nagios_host_name"]]["hoststatus"]["last_hard_state"]
//          //.'<br>Services status: '.$s[$h["nagios_host_name"]]["servicestatus"]["last_hard_state"]
//          .'<br>Combined / NagMap status: '.$s[$h["nagios_host_name"]]['status'].' : '.$s[$h["nagios_host_name"]]['status_human']
//          .'<br><a href=\"/nagios/cgi-bin/statusmap.cgi\?host='.$h["nagios_host_name"].'\">Nagios map page</a>'
//          .'<br><a href=\"/nagios/cgi-bin/extinfo.cgi\?type=1\&host='.$h["nagios_host_name"].'\">Nagios host page</a>';
//     $links = '<br><a href=\"../cgi-bin/smokeping.cgi?target=LAN.'.$h["nagios_host_name"].'\">Smokeping statistics</a>'
//          .'<br><a href=\"../devices/modules/mrtg_uptime/workdir/'.$h["nagios_host_name"].'.html\">Uptime Graph</a>';
//     if ($nagmap_bubble_links == 1) {
//       $info = $info.$links;
//     }
//     $info = $info.'<br><span style=\"font-size: 7pt\">NagMap by blava.net</span></div>';
//
//     $javascript .= ("window.".$h["host_name"]."_mark_infowindow = new google.maps.InfoWindow({ content: '$info'})\n");
//
//     $javascript .= ("google.maps.event.addListener(".$h["host_name"]."_mark, 'click', function() {"
//       .$h["host_name"]."_mark_infowindow.open(map,".$h["host_name"]."_mark);\n
//       });\n\n");

      }
   }
   echo "};\n\n";


   // ###### Make contents of the sidebar ###################################
   echo "function makeSidebarContents() {\n";
   $sitesContent = "";
   $problems = 0;
   $addedProblemsSection = false;
   foreach (array('critical', 'warning', 'unknown', 'ok') as $severity) {
      $categoryContent = "";
      foreach ($hosts as $h) {
         if ((isset($h["latlng"])) and (isset($h["host_name"]))) {
            $site       = $h["nagios_host_name"];
            $siteStatus = $status[$site]["hoststatus"]["last_hard_state"];

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
               $sitesContent = $sitesContent . '<h3 id="sites.problems">Problems</h3>';
               $addedProblemsSection = true;
            }
         }
         else if ($severity == 'ok') {
            $sitesContent = $sitesContent . '<h3 id="sites.okay">Okay</h3>';
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

   echo "</script>\n\n";
?>


    <script type="text/javascript">

    //static code from index.pnp
    function initialize() {
      var myOptions = {
        zoom: <?php echo ("$nagmap_map_zoom"); ?>,
        center: new google.maps.LatLng(<?php echo $nagmap_map_centre ?>),
        mapTypeId: google.maps.MapTypeId.<?php echo $nagmap_map_type ?>
      };
      window.map = new google.maps.Map(document.getElementById("map_canvas"),myOptions);

      //defining marker images
      var red_blank = new google.maps.MarkerImage(
        'http://www.google.com/mapfiles/marker.png',
        new google.maps.Size(20,34),
        new google.maps.Point(10,34));

      var blue_blank = new google.maps.MarkerImage(
        'http://www.google.com/mapfiles/marker_white.png',
        new google.maps.Size(20,34),
        new google.maps.Point(10,34));

      var green_blank = new google.maps.MarkerImage(
        'http://www.google.com/mapfiles/marker_green.png',
        new google.maps.Size(20,34),
        new google.maps.Point(10,34));

      var yellow_blank = new google.maps.MarkerImage(
        'http://www.google.com/mapfiles/marker_yellow.png',
        new google.maps.Size(20,34),
        new google.maps.Point(10,34));

      var grey_blank = new google.maps.MarkerImage(
        'http://www.google.com/mapfiles/marker_grey.png',
        new google.maps.Size(20,34),
        new google.maps.Point(10,34));


      makeSidebarContents();
      makeMapContents();

// generating dynamic code from here...
// if the page ends here, there is something seriously wrong, please contact maco@blava.net for help

<?php
//   if ($javascript != "") {
//     echo $javascript;
    echo '};'; //end of initialize function
    echo '
      </script>
      </head>
      <body style="margin:0px; padding:0px;" onload="initialize()">';
    echo '
      <! -- BEGIN NorNet -->
      <h1 style="margin:0px; padding:0px;">Velkommen til NorNet Kontrollsenter på Simula, Fornebu</h1>
      <! -- END NorNet -->
    ';
    if ($nagmap_sidebar == '1') {
      echo '<div id="map_canvas" style="width:80%; height:95%; float: left"></div>';
      echo '<div id="sidebar" class="sidebar" style="padding-left: 10px; height:95%; overflow:auto;">';
      echo '   <span id="sidebar.sites.problems"><ul><li>Test!</li></ul></span>';
      echo '   <span id="sidebar.sites.okay"><ul><li>Test2!</li></ul></span>';
      echo '</dev>';
    } else {
      echo '<div id="map_canvas" style="width:100%; height:100%; float: left"></div>';
    }
//   } else {
//
//     echo '};'; //end of initialize function
//     echo '</script><head><body>';
//     echo "<br><h3>There is no data to display. You either did not set NagMap properly or there is a software bug. Please contact maco@blava.net for free assistance.</h3>";
//   }

?>

</body>
</html>

