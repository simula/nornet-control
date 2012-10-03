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

function getNorNetStatus() {
  include('config.php');
  $fp = fopen($nagios_status_dat_file, "r");

  $hostName    = "";
  $serviceName = "";
  $entryType   = "";
  $status      = Array();
  while (!feof($fp)) {
      // ====== Read line from status.dat ===================================
      $line = trim(fgets($fp));

      // ====== Handle line =================================================
      if ( (empty($line)) ||
           (preg_match("/^;/", $line)) ||
           (preg_match("/^#/", $line)) ) {
         // Ignore empty line or comment.
      }
      elseif (preg_match("/}/",$line)) {
         // End of entry
         $hostName    = "";
         $serviceName = "";
      }
      elseif (preg_match("/^hoststatus {/", $line)) {
         $entryType = "hoststatus";
      }
      elseif (preg_match("/^servicestatus {/", $line)) {
         $entryType = "servicestatus";
      }
      elseif ( (!preg_match("/}/", $line)) &&
              (($entryType == "hoststatus") || ($entryType == "servicestatus")) ) {
         $line   = trim($line);
         $pieces = explode("=", $line, 2);
         if (count($pieces) >= 2) {
            $parameterName = trim($pieces[0]);
            $value         = trim($pieces[1]);
            if ($parameterName == "host_name") {
               $hostName    = $value;
               $serviceName = "";
            }
            elseif ($parameterName == "service_description") {
               $serviceName = $value;
            }
            elseif ( ($parameterName == "last_hard_state") ||
                     ($parameterName == "plugin_output")  ||
                     ($parameterName == "performance_data") ||
                     ($parameterName == "check_command") ) {
               if (!isset($status[$hostName][$serviceName]['last_hard_state'])) {
                  // Initialize state with empty string, just for the case it
                  // is missing in status.dat.
                  $status[$hostName][$serviceName]['last_hard_state'] = "";
               }

               // ====== NorNet-specific service handling ===================
               if ($parameterName == "check_command") {
                  // ====== Handle site =====================================
                  if (preg_match("/^MySiteCheck!/", $value)) {
                     $value = preg_replace("/^MySiteCheck!/", "", $value);
                     $args  = str_getcsv($value, ' ');
                     echo $args;
                  }

                  // ====== Handle tunnel ===================================
                  elseif (preg_match("/^MyTunnelCheck!/", $value)) {
                     $value = preg_replace("/^MyTunnelCheck!/", "", $value);
                     $args  = str_getcsv($value, ' ');
                     $localHostName  = "";
                     $remoteHostName = "";
                     for ($i = 0; $i < count($args); $i++) {
                        if ($args[$i] == "-L") {
                           $localHostName = $args[$i + 1];
                           $i++;
                        }
                        else if ($args[$i] == "-R") {
                           $remoteHostName = $args[$i + 1];
                           $i++;
                        }
                     }
                     $status[$hostName][$serviceName]['local_host_name']  = $localHostName;
                     $status[$hostName][$serviceName]['remote_host_name'] = $remoteHostName;
                  }
               }

               $status[$hostName][$serviceName][$parameterName] = $value;
            }
         }
      }
   }

   foreach ($status as $hostName => $hostEntry) {
      foreach ($hostEntry as $serviceName => $serviceEntry) {
         foreach ($serviceEntry as $parameterName => $parameterEntry) {
            echo "<br />".$hostName.".".$serviceName.".".$parameterName." = ".$parameterEntry;
         }
      }
   }

  return $status;
}

echo "Test1\n";

$status = getNorNetStatus();

echo "<br/>Test2\n";

?>

</body>
</html>
