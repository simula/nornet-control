<?php
define('BASE_URL', dirname($_SERVER['SCRIPT_NAME']));
function get_path() {
   return str_replace('\\', '/', dirname($_SERVER['REQUEST_URI']));
}
?>

<h1>NorNet Server <em><?php echo @$_SERVER['SERVER_NAME']; ?></em></h1>
<h2>Directory: <?php echo get_path(); ?></h2>
