import pygame

import gui, states, events, configscreen, api_calls

upDownElementsSignin = ["signin.registeraccount", "signin.signin", "signin.pw","signin.username"]
upDownElementsSigninIndex= -1
upDownElementsRegiser = ["register.signinaccount", "register.register", "signin.pw","signin.username","register.email"]
upDownElementsRegiserIndex= -1
username_text =""
password_text =""
email_text =""
signin_screen = True
status_text=""

def handleInput(world, event):
  invalid = False
  if event == events.btnSelectOn or event == events.btnStartOn:
    moveForward(world)

  elif event == events.btnLeftOn or event == events.btnRightOn:
    changeFocusedElm(world,event)

  elif event == events.btnUpOn or event == events.btnDownOn:
    changeFocusUpDown(world, event)

  elif event == events.btnEscapeOn:
    world.running = False

  elif (event>=1000):
    handleInputtext(world, event)

  else:
    invalid = True

  if event%10 == 1 and not invalid:
    world.sounds['uiaction'].play(0)

def handleInputtext(world, event):
  global username_text
  global password_text
  global email_text

  #backsapce
  if(event==1000):
    if (world.focused == "signin.username"):
      username_text = username_text[:-1]
    elif (world.focused == "signin.pw"):
      password_text = password_text[:-1]
    elif (world.focused == "register.email"):
      email_text = email_text[:-1]
    return


  char=""
  allChars = "abcdefghijklmnopqrstuvwxyz0123456789.@"
  char = allChars[event-1001]
  if(world.focused == "signin.username"):
    username_text += char
  elif (world.focused == "signin.pw"):
    password_text += char
  elif (world.focused == "register.email"):
    email_text += char

def changeFocusUpDown(world,event):
  global signin_screen
  global upDownElementsSigninIndex
  global upDownElementsRegiserIndex

  if(signin_screen):
    #131=up
    if(event==131):
      if(upDownElementsSigninIndex+1 == len(upDownElementsSignin)):
        return
      upDownElementsSigninIndex += 1

    #141=down
    if (event == 141):
      if (world.focused == "intro.play" or world.focused == "intro.settings"):
        return
      if (upDownElementsSigninIndex == 0):
        world.focused = "intro.play"
        upDownElementsSigninIndex -= 1
        return
      upDownElementsSigninIndex -= 1

    world.focused = upDownElementsSignin[upDownElementsSigninIndex]
  else:
    # 131=up
    if (event == 131):
      if (upDownElementsRegiserIndex + 1 == len(upDownElementsRegiser)):
        return
      upDownElementsRegiserIndex += 1

    # 141=down
    if (event == 141):
      if (world.focused == "intro.play" or world.focused == "intro.settings"):
        return
      if (upDownElementsRegiserIndex == 0):
        world.focused = "intro.play"
        upDownElementsRegiserIndex -= 1
        return
      upDownElementsRegiserIndex -= 1

    world.focused = upDownElementsRegiser[upDownElementsRegiserIndex]

def changeFocusedElm(world,event):
  if world.focused == "intro.play":
    world.focused = "intro.settings"
  elif world.focused == "intro.performance":
    world.focused = "intro.settings"
  elif world.focused == "intro.settings" and event==111:
    world.focused = "intro.performance"
  elif world.focused == "intro.settings" and event==121:
    world.focused = "intro.play"

def moveForward(world):
  global status_text
  global signin_screen
  global username_text
  global password_text
  global email_text

  if world.focused == "intro.play":
    world.state = states.Setup
  elif world.focused == "intro.settings":
    configscreen.enter(world)
  elif world.focused == "signin.registeraccount":
    username_text=""
    password_text=""
    signin_screen = False
  elif world.focused == "register.signinaccount":
    username_text=""
    password_text=""
    email_text=""
    signin_screen = True
  elif world.focused == "signin.signin":
    status_text = api_calls.call_signin(username_text,password_text)
  elif world.focused == "register.register":
    status_text = api_calls.call_register(email_text,username_text,password_text)

def draw( world ):
  r = world.worldsurf_rect
  world.worldsurf.fill( world.bg_color )

  logo_rect = world.logo.get_rect()
  logo_rect.centerx = r.centerx
  logo_rect.top = 80
  world.worldsurf.blit( world.logo, logo_rect )

  gclogo_rect = world.gclogo.get_rect()
  gclogo_rect.bottom = r.bottom - 20
  gclogo_rect.centerx = r.centerx
  world.worldsurf.blit( world.gclogo, gclogo_rect )

  if(not signin_screen):
    gui.simpleText(world, "Email :", 266, 30)

    if(len(email_text)>22):
      email_text_show=email_text[len(email_text)-22:]
    else:
      email_text_show=email_text

    gui.textInput(world, email_text_show, 310, 22, 250, 20, world.focused == "register.email")

    gui.button(world, "REGISTER", 440, 120, 120, 32,
      world.focused == "register.register"
    )

    gui.button(world, "Sign in to an account", 240, 170, 320, 22,
      world.focused == "register.signinaccount"
    )

  gui.simpleText(world, status_text, 280, 140, (255,0,0))

  gui.simpleText(world, "Username :", 290, 60)
  gui.simpleText(world, "Password  :", 290, 90)

  if (len(username_text) > 16):
    username_text_show = username_text[len(username_text) - 16:]
  else:
    username_text_show = username_text
  gui.textInput(world, username_text_show, 360, 52, 200, 20 ,world.focused == "signin.username")

  if (len(password_text) > 16):
    password_text_show = password_text[len(password_text) - 16:]
  else:
    password_text_show = password_text
  gui.textInput(world, password_text_show, 360, 82, 200, 20 ,world.focused == "signin.pw")

  if (signin_screen):
    gui.button(world, "SIGN IN", 440, 120, 120, 32,
      world.focused == "signin.signin"
    )

    gui.button(world, "Register new account", 240, 170, 320, 22,
      world.focused == "signin.registeraccount"
    )



  gui.button(world, "PERFORMANCE", r.centerx - 360, r.bottom - 210, 160, 51,
    world.focused == "intro.performance"
  )

  gui.button(world, "SETTINGS", r.centerx-160, r.bottom-210, 160, 51,
    world.focused == "intro.settings"
  )
  gui.button(world, "PLAY", r.centerx+40, r.bottom-210, 120, 51,
    world.focused == "intro.play"
  )

  txty = r.height - gclogo_rect.height - 40
  if world.moment >= world.textBlinkLastTime + 0.7:
    btnName = "START" if pygame.joystick.get_count() > 0 else "Enter"
    actName = " to begin" if world.focused == "intro.play" else " for settings"
    gui.textSurface("Press " + btnName + actName,
      world.scores_font, ( 200, 200, 200 ),
      ( r.centerx, txty ),
      world.worldsurf
    )
    if world.moment >= world.textBlinkLastTime + 2:
      world.textBlinkLastTime = world.moment
