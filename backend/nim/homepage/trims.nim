proc trmdefault(rec:HomePage, ctx:Ctx) :string =
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
  """<main class="n9">""" & 
  """<div class="n10">""" & 
  """<div>""" & 
  """<h1>""" & 
   & "How to Play Metatris <small>(and improve)</small>" & 
  "</h1>" & 
  """<h2>""" & 
   & "KEEP IT IN THE GREEN" & 
  "</h2>" & 
  """<p>""" & 
   & "This is a Beta version of the Metatris program. Metatris was inspired by Meta-T which scientists have been using to study tetris players of all skill levels since 2015. At the moment the game is geared towards the playing style of Classic NES. However, we are hoping for future versions to include the principles and provide a version that supports modern/guideline Tetris. Your job is simple, the years of data collection have been developed into a tool that will give you real live feedback as you play. To make it simple, KEEP IT IN THE GREEN." & 
  "</p>" & 
  """<p>""" & 
   & "The bar to the right of the screen moves up and down, when it is high in the green your piece play was great, as it lowers into yellow and red, you know that your piece movements and placements were not good. An average “Metascore” will tell you how you are doing over the course of the game. It’s very simple. The more you keep the bar in the green the better your score will be." & 
  "</p>" & 
  """<h3>""" & 
   & "What the game does" & 
  "</h3>" & 
  """<p>""" & 
   & "The game is not designed to teach you to play faster, instead it is designed to teach you to be efficient and to stack better, which we know is the skill that underlies great Tetris play for all types. You will not be rewarded for finesse moves (in this current beta version) or for hard dropping pieces quickly, or for speed runs. <em>You will be rewarded for expert piece placements and efficient movements.</em>" & 
  "</p>" & 
  """<p>""" & 
   & "This is a great way to equalize the difference between DAS and Hypertap players because the Metascore is not purely based on number of Tetrises but instead <em>efficiency and lack of waste</em>. In other words, when you play against an opponent or compare performance Metascore is an indicator based on science that can tell you and everyone how good you are." & 
  "</p>" & 
  """<h3>""" & 
   & "How to judge your performance" & 
  "</h3>" & 
  """<p>""" & 
   & "A Metascore of 0 is a perfect score. This will almost never be attained. The worst possible score is over 100. Your job is to keep the moving bar in the green. The bar and the numbers inside the gameboard will change with every game interaction to let you know how you performed for that particular game piece. The Metascore to the right of the gameboard, underneath the next box, is your <em>overall average</em> for the entire game. Try to keep both as low as possible." & 
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