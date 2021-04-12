proc trmdefault(rec:Connection, ctx:Ctx) :string =
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
  """<main class="n25">""" & 
  """<div class="n26">""" & 
  """<h1 class="n27">""" & "Metatris Game Login" & 
  "</h1>" & 
  """<p class="n28">""" & "Please compare the number below with the one you see on the game window. If numbers match, please confirm Metatris Game login." & 
  "</p>" & 
  """<p class="n29">""" & 
  (if rec.appkey.len == 6: """<span>""" & rec.appkey[0] & 
  "</span>" & 
  """<span>""" & rec.appkey[1] & 
  "</span>" & 
  """<span>""" & rec.appkey[2] & 
  "</span>" & 
  """<span>""" & rec.appkey[3] & 
  "</span>" & 
  """<span>""" & rec.appkey[4] & 
  "</span>" & 
  """<span>""" & rec.appkey[5] & 
  "</span>" else: """<span>""" & 
   & "token invalid!" & 
  "</span>") & 
  "</p>" & 
  """<form class="n30">""" & 
  """<button class="n31" mh="click:reject-app-login">""" & "Reject" & 
  "</button>" & 
  """<button class="n32" mh="click:approve-app-login">""" & "Confirm" & 
  "</button>" & 
  "</form>" & 
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