proc trmdefault(rec:DownloadPage, ctx:Ctx) :string =
  """<!DOCTYPE html>""" & 
  """<html lang="en">""" & 
  """<head>""" & 
  """<meta charset="UTF-8">""" & 
  """<title>""" & 
   & "Metatris" & 
  "</title>" & 
  """<meta name="viewport" content="width=device-width, initial-scale=1.0">""" & 
  """<link rel="stylesheet" href="//metatris-media.mond.red/css/main.css">""" & 
  """<meta name="description" content="Metatris Community Official Homepage">""" & 
  """<link rel="icon" href="//metatris-media.mond.red/favicon.ico">""" & 
  "</head>" & 
  """<body>""" & 
  """<header class="n1">""" & 
  """<div class="n2">""" & 
  """<div class="n3">""" & 
  """<img class="n4" src="//metatris-media.mond.red/logo-bar.svg" alt="Metatris Logo">""" & 
  "</div>" & 
  """<div class="n5">""" & 
  (if ctx.owner != nil: """<a class="n6" href="#" mh="click:logout">""" & 
  """<img class="n7" src="//metatris-media.mond.red/ui/exit.svg" alt="Sign Out">""" & 
  "</a>" else: "") & 
  "</div>" & 
  "</div>" & 
  """<div class="n8">""" & 
  """<a href="/">""" & "The Game" & 
  "</a>" & 
  """<a href="/download">""" & "Download" & 
  "</a>" & 
  """<a href="/the-team">""" & "The Team" & 
  "</a>" & 
  "</div>" & 
  "</header>" & 
  """<main class="n12">""" & 
  """<div class="n13">""" & 
  """<h1 class="n14">""" & "Welcome to Metatris!" & 
  "</h1>" & 
  (if ctx.owner == nil: """<form class="n15" mh="submit:login">""" & 
  """<h3>""" & 
   & "Member Login" & 
  "</h3>" & 
  """<input type="text" autocomplete="username" placeholder="Username" m="fol">""" & 
  """<input type="password" autocomplete="current-password" placeholder="Password">""" & 
  """<input class="n16" type="submit" value="Login">""" & 
  "</form>" else: """<div class="n17" mh="click:download" mh-download="metatris.0.1.1.msi">""" & 
  """<div class="n18">""" & 
  """<img width="90" src="//metatris-media.mond.red/ui/download.svg">""" & 
  "</div>" & 
  """<div>""" & 
  """<h2>""" & 
   & "Download Installer" & 
  "</h2>" & 
  """<p class="n19">""" & "Version: 0.1.1" & 
  "</p>" & 
  "</div>" & 
  "</div>") & 
  "</div>" & 
  "</main>" & 
  """<footer class="n11">""" & 
  """<div>""" & 
   & "Metatris &copy; 2020" & 
  "</div>" & 
  "</footer>" & 
  """<script src="//metatris-media.mond.red/js/download.js">""" & 
  "</script>" & 
  """<script src="//metatris-media.mond.red/js/main.js">""" & 
  "</script>" & 
  "</body>" & 
  "</html>"