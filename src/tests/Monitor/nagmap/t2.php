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
  $fp = fopen($nagios_status_dat_file,"r");
  $type = "";
  $data = Array();
  while (!feof($fp)) {
    $line = trim(fgets($fp));
    //ignore all commented lines - hop to the next itteration
    if (empty($line) OR preg_match("/^;/", $line) OR preg_match("/^#/", $line)) {
      continue;
    }
    //if end of definition, skip to next itteration
    if (preg_match("/}/",$line)) {
      $type = "0";
      unset($host);
      continue;
    }
    if (preg_match("/^hoststatus {/", $line)) {
      $type = "hoststatus";
    };
    if (preg_match("/^servicestatus {/", $line)) {
      $type = "servicestatus";
    };
    if(!preg_match("/}/",$line) && ($type == "hoststatus" | $type == "servicestatus")) {
      $line = trim($line);
      $pieces = explode("=", $line, 2);
      //do not bother with invalid data
      if (count($pieces) < 2) { continue; };
      $option = trim($pieces[0]);
      $value  = trim($pieces[1]);
      if ($option == "host_name") {
        $host = $value;
      }
      else if( ($option != "last_hard_state") &&
               ($option != "plugin_output") &&
               ($option != "performance_data") &&
               ($option != "service_description") &&
               ($option != "check_command") ) {
         continue;
      }
      echo "Add: H=".$host." T=".$type." -> ".$option."=".$value."<br />\n";
      if (!isset($data[$host][$type][$option])) {
        $data[$host][$type][$option] = "";
      }

      if (!isset($data[$host]['servicestatus']['last_hard_state'])) {
        $data[$host]['servicestatus']['last_hard_state'] = "";
      }

      if ($option == "last_hard_state") {
        if ($value >= $data[$host][$type][$option]) {
          $data[$host][$type][$option] = $value;
        }
        if (($data[$host]['hoststatus']['last_hard_state'] == 0) && ($data[$host]['servicestatus']['last_hard_state'] == 0)) {
          $data[$host]['status'] = 0;
          $data[$host]['status_human'] = 'OK';
          $data[$host]['status_style'] = 'ok';
        } elseif (($data[$host]['hoststatus']['last_hard_state'] == 2) | ($data[$host]['servicestatus']['last_hard_state'] == 1)) {
          $data[$host]['status'] = 1;
          $data[$host]['status_human'] = 'WARNING / UNREACHABLE';
          $data[$host]['status_style'] = 'warning';
        } elseif (($data[$host]['hoststatus']['last_hard_state'] == 1) | ($data[$host]['servicestatus']['last_hard_state'] == 2)) {
          $data[$host]['status'] = 2;
          $data[$host]['status_human'] = 'CRITICAL / DOWN';
          $data[$host]['status_style'] = 'critical';
        } else {
          $data[$host]['status'] = 3;
          $data[$host]['status_human'] = 'UNKNOWN - NagMap bug - please report to maco@blava.net !';
          $data[$host]['status_style'] = 'critical';
        }
      }
    }
  }
  return $data;
}

echo "Test1\n";

$s = getNorNetStatus();
echo $s;

echo "Test2\n";

?>

</body>
</html>
