proc trmdefault(rec:TeamPage, ctx:Ctx) :string =
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
  """<main class="n20">""" & 
  """<div class="n21">""" & 
  """<div>""" & 
  """<h1>""" & 
   & "The Team" & 
  "</h1>" & 
  """<h2>""" & 
   & "About the Scientist" & 
  "</h2>" & 
  """<img class="n22" width="2400" height="2400" src="//metatris-media.mond.red/team/jackie.jpg">""" & 
  """<p>""" & 
   & "Dr. Jackie Berry attended Rensselaer for a BS in psychology, an MS in psychology, and an MBA. After graduating she worked for a software company for a few years and then attended the University at Albany, SUNY for a Ph.D. in Cognitive Psychology. After working for a startup company, she returned to academia as a Psychology Professor for several years. She then returned to Rensselaer Polytechnic Institute to research how people become experts, and attended the CTWC in 2017 and 2018 to study the expert Tetris players there. In 2019 she went to Egypt as a Fulbright scholar where she taught a class on how to become an expert and conducted Tetris research on Egyptian college students. She returned home at the beginning of the COVID pandemic and began putting her knowledge of tetris and expertise into the Metatris tool." & 
  "</p>" & 
  """<p>""" & 
   & "Dr. Berry has been playing Tetris for 31 years and has a patent pending for the technology used to develop the Game Changer Metatris tool. She recently attempted to qualify for the CTWC 2020. You can find her not playing very well on twitch at" & 
   & " " & 
  """<a href="https://twitch.tv/jack13berry" target="_blank">""" & "twitch.tv/jack13berry" & 
  "</a>" & 
  """<div>""" & 
  "</div>" & 
  "</p>" & 
  """<h2 class="n23">""" & "About the Developer" & 
  "</h2>" & 
  """<img class="n24" width="2400" height="2400" src="//metatris-media.mond.red/team/hasan.jpg">""" & 
  """<p>""" & 
   & "Hasan Yasin Ozturk..." & 
  "</p>" & 
  "</div>" & 
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