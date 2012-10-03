<?php
//
// NorNet Status Reader
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


# ###### Obtain NorNet status from Nagios's status.dat file =================
function getNorNetStatus() {
   include('NorNet-Configuration.php');

   $hostName    = "";
   $serviceName = "";
   $entryType   = "";
   $status      = Array();

   $fp = fopen($NorNet_Nagios_Status, "r");
   if (!$fp) {   // Cannot read file!
     echo "ERROR!";
     return $status;
   }

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
                     $location = "";
                     for ($i = 0; $i < count($args); $i++) {
                        if ($args[$i] == "-L") {
                           $location = $args[$i + 1];
                           $i++;
                        }
                     }
                     $status[$hostName][$serviceName]['location']  = $location;
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
                     $status[$hostName][$serviceName]['tunnel_local_host_name']  = $localHostName;
                     $status[$hostName][$serviceName]['tunnel_remote_host_name'] = $remoteHostName;
                  }
               }

               $status[$hostName][$serviceName][$parameterName] = $value;
            }
         }
      }
   }

//    foreach ($status as $hostName => $hostEntry) {
//       foreach ($hostEntry as $serviceName => $serviceEntry) {
//          foreach ($serviceEntry as $parameterName => $parameterEntry) {
//             echo "<br />".$hostName.".".$serviceName.".".$parameterName." = ".$parameterEntry."\n";
//          }
//       }
//    }

  return $status;
}

?>
