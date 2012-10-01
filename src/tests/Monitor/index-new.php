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

   echo "<script>\n";

   include('marker.php');

   echo "function makeMapContents() {\n";
   echo "}\n\n";


   echo "function makeSidebarContents() {\n";
   $status = nagmap_status();

   $sitesContent = "";
   $problems = 0;
   foreach (array('critical', 'warning', 'unknown', 'ok') as $severity) {
      $categoryContent = "";
      foreach ($hosts as $h) {
         if ((isset($h["latlng"])) and (isset($h["host_name"]))) {
            $site = $h['nagios_host_name'];

            if( ($severity == "critical") &&
                ($status[$site] == 2) ) {
               $categoryContent = $categoryContent . '<li class="critical"><blink><strong>&#9760;</strong></blink>' . $site . '</li>';
               $problems++;
            }
            elseif( ($severity == "warning") &&
                ($status[$site] == 1) ) {
               $categoryContent = $categoryContent . '<li class="warning">&#9785;' . $site . '</li>';
               $problems++;
            }
            elseif( ($severity == "unknown") &&
                    ($status[$site] > 2) ) {
               $categoryContent = $categoryContent . '<li class="unknown">&#128528;' . $site . '</li>';
            }
            elseif( ($severity == "ok") &&
                    ($status[$site] == 0) ) {
               $categoryContent = $categoryContent . '<li class="ok">&#9786;' . $site . '</li>';
            }
         }
      }
      $sitesContent = $sitesContent . $categoryContent;
   }
   echo "   document.getElementById(\"sidebar.sites.content\").innerHTML = '" . $sitesContent . "';\n";

   echo "}\n\n";

   echo "</script>\n\n";
?>


    <script type="text/javascript">

    //static code from index.pnp
    function initialize() {
      makeSidebarContents();
      makeMapContents();

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


// generating dynamic code from here...
// if the page ends here, there is something seriously wrong, please contact maco@blava.net for help

<?php
  if ($javascript != "") {
    echo $javascript;
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
      sort($sidebar['ok']);
      sort($sidebar['warning']);
      sort($sidebar['critical']);
      sort($sidebar['unknown']);
      echo '<div id="map_canvas" style="width:80%; height:95%; float: left"></div>';
      echo '<div id="sidebar" class="sidebar" style="padding-left: 10px; height:95%; overflow:auto;">';
      echo '   <span id="sidebar.sites.content"><ul><li>Test!</li></ul></span>';
      echo '   <span id="sidebar.sites.content2"><ul><li>Test2!</li></ul></span>';
      echo '</dev>';
    } else {
      echo '<div id="map_canvas" style="width:100%; height:100%; float: left"></div>';
    }
  } else {

    echo '};'; //end of initialize function
    echo '</script><head><body>';
    echo "<br><h3>There is no data to display. You either did not set NagMap properly or there is a software bug. Please contact maco@blava.net for free assistance.</h3>";
  }

?>

</body>
</html>

