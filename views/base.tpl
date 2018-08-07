<!DOCTYPE html>

<html>
<title>Rod Dveh Rek</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="/static/uvodna.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<style>
body {font-family: "Lato", sans-serif}
</style>

<body>

<!-- Navbar -->
<div class="w3-top">
  <div class="w3-bar w3-green w3-card">
    <a class="w3-bar-item w3-button w3-padding-large w3-hide-medium w3-hide-large w3-right" href="javascript:void(0)" onclick="myFunction()" title="Toggle Navigation Menu"><i class="fa fa-bars"></i></a>
    <a href="#" class="w3-bar-item w3-button w3-padding-large">DOMOV</a>

    <!-- to je za uvodno stran-->
    %if stil == 'uvodna':
    <a href="#rdr" class="w3-bar-item w3-button w3-padding-large w3-hide-small">RDR</a>
    <a href="#akcije" class="w3-bar-item w3-button w3-padding-large w3-hide-small">AKCIJE</a>
    <a href="#kontakt" class="w3-bar-item w3-button w3-padding-large w3-hide-small">KONTAKT</a>
    <a href="/prijava/" class="w3-bar-item w3-button w3-padding-large">PRIJAVA</a>
  </div>
</div>

<!-- Navbar on small screens (remove the onclick attribute if you want the navbar to always show on top of the content when clicking on the links) -->
<div id="navDemo" class="w3-bar-block w3-green w3-hide w3-hide-large w3-hide-medium w3-top" style="margin-top:46px">
  <a href="#rdr" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">RDR</a>
  <a href="#akcije" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">AKCIJE</a>
  <a href="#kontakt" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">KONTAKT</a>
</div>
%end

<!-- to je za starša -->
%if stil == 'stars':
    <a href="#rdr" class="w3-bar-item w3-button w3-padding-large w3-hide-small">RDR</a>
    <a href="#akcije" class="w3-bar-item w3-button w3-padding-large w3-hide-small">AKCIJE</a>
    <a href="#clanarina" class="w3-bar-item w3-button w3-padding-large w3-hide-small">ČLANARINA</a>
    <a href="#vpis" class="w3-bar-item w3-button w3-padding-large w3-hide-small">VPIS</a>
    <a href="#kontakt" class="w3-bar-item w3-button w3-padding-large w3-hide-small">KONTAKT</a>
    <a href="/odjava/" class="w3-bar-item w3-button w3-padding-large">ODJAVA</a>
  </div>
</div>

<!-- Navbar on small screens (remove the onclick attribute if you want the navbar to always show on top of the content when clicking on the links) -->
<div id="navDemo" class="w3-bar-block w3-green w3-hide w3-hide-large w3-hide-medium w3-top" style="margin-top:46px">
  <a href="#rdr" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">RDR</a>
  <a href="#akcije" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">AKCIJE</a>
  <a href="#clanarina" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">ČLANARINA</a>
  <a href="#vpis" class="w3-bar-item w3-button w3-padding-large">VPIS</a>
  <a href="#kontakt" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">KONTAKT</a>
</div>
%end


<!-- to je za admina -->
%if stil == 'admin':
    <a href="#člani" class="w3-bar-item w3-button w3-padding-large w3-hide-small">ČLANI</a>
    <a href="#akcije" class="w3-bar-item w3-button w3-padding-large w3-hide-small">AKCIJE</a>
    <a href="#vodi" class="w3-bar-item w3-button w3-padding-large w3-hide-small">VODI</a>
    <a href="#išči" class="w3-bar-item w3-button w3-padding-large w3-hide-small">IŠČI</a>
    <a href="#članarina" class="w3-bar-item w3-button w3-padding-large w3-hide-small">ČLANARINA</a>
    <a href="/odjava/" class="w3-bar-item w3-button w3-padding-large">ODJAVA</a>
  </div>
</div>

<!-- Navbar on small screens (remove the onclick attribute if you want the navbar to always show on top of the
content when clicking on the links) -->
<div id="navDemo" class="w3-bar-block w3-green w3-hide w3-hide-large w3-hide-medium w3-top" style="margin-
top:46px">
    <a href="#člani" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">ČLANI</a>
    <a href="#akcije" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">AKCIJE</a>
    <a href="#vodi" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">VODI</a>
    <a href="#išči" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">IŠČI</a>
    <a href="#članarina" class="w3-bar-item w3-button w3-padding-large" onclick="myFunction()">ČLANARINA</a>
</div>
%end

<!-- Page content -->
<div class="w3-content" style="max-width:2000px;margin-top:46px">

%if slika==True:
<style>
img {
    display: block;
    margin-left: auto;
    margin-right: auto;
}
</style>
  <!-- Image -->
  <img src="/static/img/RDRgrb.jpg" style="width:30%" class="center">
%end


{{!base}}

<!-- Footer -->
<footer class="w3-container w3-padding-64 w3-center w3-opacity w3-light-grey w3-xlarge">
        <div class="text-center">
         <small> <p>&copy; Copyright
        <script language="JavaScript" type="text/javascript">
            now = new Date
            theYear=now.getYear()
            if (theYear < 1900)
            theYear=theYear+1900
            document.write(theYear)
        </script>
         </small>
        </div>
    </footer>

    </body>
    </html>