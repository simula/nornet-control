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

<script src="http://maps.google.com/maps/api/js?sensor=false" type="text/javascript"></script>
<script src="NorNet-Map.php" type="text/javascript"></script>
<script src="NorNet-Kontrollsenter.js" type="text/javascript"></script>
</head>

<body>

<div id="header" class="header">
 <h1 style="margin: 0px; padding: 0px;" id="header.title">&nbsp;</h1>
</div>

<div id="map_canvas" class="map" style="height: 100%;">
 <noscript>
  <h2>NorNet Map requires JavaScript!</h2>
 </noscript>
</div>

<div id="sidebar" class="sidebar">
 <h2 style="text-align: center;">
  <p class="center">
  <a href="javascript:" onclick="displayLanguage='NO'; updateDisplay();"><img src="graphics/flags/flag-norway.png" alt="Norsk" width="32" /></a>
  <a href="javascript:" onclick="displayLanguage='EN'; updateDisplay();"><img src="graphics/flags/flag-england.png" alt="English" width="32" /></a>
  <a href="javascript:" onclick="displayLanguage='DE'; updateDisplay();"><img src="graphics/flags/flag-germany.png" alt="Deutsch" width="32" /></a>
  </p>
 </h2>
 <hr />

<!--  <h2 id="sidebar.clock">Time</h2> -->
  <p class="center">
  <object id="analog-clock" class="clock" data="station-clock.svg" type="image/svg+xml">
   <param name="dial"               value="din 41091.1"/>
   <param name="hourHand"           value="siemens"/>
   <param name="minuteHand"         value="siemens"/>
   <param name="secondHand"         value="din 41071.2"/>
   <param name="minuteHandBehavior" value="stepping"/>
   <param name="secondHandBehavior" value="swinging"/>
   <param name="secondHandStopToGo" value="yes"/>
   <param name="secondHandStopTime" value="1.5"/>
   <param name="backgroundColor"    value="rgba(0,0,0,0)"/>
   <param name="dialColor"          value="rgb(40,40,40)"/>
   <param name="hourHandColor"      value="rgb(20,20,20)"/>
   <param name="minuteHandColor"    value="rgb(20,20,20)"/>
   <param name="secondHandColor"    value="rgb(160,50,40)"/>
   <param name="axisCoverColor"     value="rgb(20,20,20)"/>
   <param name="axisCoverRadius"    value="7"/>
   <param name="updateInterval"     value="50"/>
  </object>
  <br />
  <span id="clock" class="time">--:--:--</span><br />
  <span id="date" class="date">--</span>
  </p>
 <hr />

 <h2 id="sidebar.sites">Sites</h2>
  <h3 id="sidebar.sites.problems.title">Problems</h3>
   <span id="sidebar.sites.problems"></span>
  <h3 id="sidebar.sites.okay.title">Okay</h3>
   <span id="sidebar.sites.okay"></span>

</div>

<div id="footer" class="footer">
 <p class="footer" style="margin: 0px; padding: 0px;" id="footer.title">&nbsp;</p>
</div>

</body>

</html>
