<p class="description">
This server is part of the <a href="https://www.nntb.no/">NorNet</a>
testbed build infrastructure. Please have a look at
<a href="https://www.nntb.no/">https://www.nntb.no/</a> for details!
</p>

<p class="description">
 
<?php
date_default_timezone_set('UTC');
$server = @$_SERVER['SERVER_NAME'];
echo date("D M j G:i:s T Y");
echo " – ";
echo "<a href=\"http://" . @$server . "\">" . @$server . "</a>";
?>

</p>
