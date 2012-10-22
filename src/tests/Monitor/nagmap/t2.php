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

</head>

<body>

<?php

include('NorNet-Status.php');

echo "Test1\n";

$status = getNorNetStatus();

echo "<br/>Test2\n";

   foreach ($status as $hostName => $hostEntry) {
      if (isset($status[$hostName][""]["location"])) {
         echo "<br />Host ".$hostName." at ".$status[$hostName][""]["location"]."\n";
      }
   }

   foreach ($status as $hostName => $hostEntry) {
      foreach ($hostEntry as $serviceName => $serviceEntry) {
         if ($serviceName != "") {   // A real service!
            if ( (isset($status[$hostName][$serviceName]["tunnel_local_host_name"])) &&
                 (isset($status[$hostName][$serviceName]["tunnel_remote_host_name"])) ) {
               $tunnelState    = $status[$hostName][$serviceName]['last_hard_state'];
               $localHostName  = $status[$hostName][$serviceName]['tunnel_local_host_name'];
               $remoteHostName = $status[$hostName][$serviceName]['tunnel_remote_host_name'];
               echo "<br />Tunnel ".$localHostName." to ".$remoteHostName." S=".$tunnelState."\n";
            }
         }
      }
   }

echo "<br/>Test3\n";

?>

</body>
</html>
