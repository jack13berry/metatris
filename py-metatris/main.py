# Based on the work by John K. Lindstedt

import sys, os

import argparse
import pygame
import time

from world import World
import cnf
import configselect
import paths


def initialize_pygame():
  pygame.init()
  try:
    pygame.mixer.init()
  except pygame.error:
    pygame.mixer.quit()
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    pygame.mixer.init()


def between_zero_and_one( string ):
  value = float( string )
  if value < 0 or value > 1:
    msg = "%r is not between 0.0 and 1.0 " % string
    raise argparse.ArgumentTypeError( msg )
  return value


def date_time_filename():
  namestring = ""
  date = time.localtime()
  namestring += str( date.tm_year ) + "-"
  namestring += str( date.tm_mon ) + "-"
  namestring += str( date.tm_mday ) + "_"
  namestring += str( date.tm_hour ) + "-"
  namestring += str( date.tm_min ) + "-"
  namestring += str( date.tm_sec )
  #namestring += ".tsv"
  return namestring


def main():
  paths.initialize_configs(cnf.CONFIG_DIR)
  parser = argparse.ArgumentParser( formatter_class = argparse.ArgumentDefaultsHelpFormatter )

  parser.add_argument('-c', '--config', choices=cnf.available_configs(),
    help='Use a config by name, skipping the startup picker. Each profile overrides default.config.')
  parser.add_argument('--self-test', action='store_true',
    help='Check all bundled study profiles, controls, displays, timers, and saved data without network uploads.')

  parser.add_argument( '-L', '--logfile',
    action = "store", dest = "logfile", default = date_time_filename(),
    help = 'Pipe results to given filename; "[year_month_day_hour-min-sec].tsv" by default.' )

  parser.add_argument( '-d', '--logdir',
    action = "store", dest = "logdir",
    help = 'Logging directory; "./data" by default.' )

  parser.add_argument( '-F', '--fullscreen',
    action = "store", dest = "fullscreen",
    type = cnf.is_true,
    help = 'Run in fullscreen mode (true/false); default.config turns it on.' )

  parser.add_argument( '-s', '--song',
    action = "store", dest = "song",
    choices = ['gb-a', 'gb-b', 'nes-a', 'nes-b', 'nes-c'],
    help = 'Background song/music to play.' )

  parser.add_argument( '--music_vol',
    action = "store", dest = "music_vol",
    type = between_zero_and_one,
    help = 'Set music volume.' )

  parser.add_argument( '--sfx_vol',
    action = "store", dest = "sfx_vol",
    type = between_zero_and_one,
    help = 'Set sound effects volume.' )

  parser.add_argument( '-wd', '--width',
    action = "store", dest = "game_wd",
    type = int,
    help = "Sets width of game board; 10 by default (change to 16 for Pentix default)")

  parser.add_argument( '-ht', '--height',
    action = "store", dest = "game_ht",
    type = int,
    help = "Sets height of game board; 20 by default (change to 25 for Pentix default)")

  parser.add_argument( '-la', '--lookahead',
    action = "store", dest = "look_ahead",
    type = int,
    help = "Sets look-ahead, i.e. next box; 0 = none, 1 = default, 2... = not yet implemented")

  parser.add_argument( '-g', '--gravity',
    action = "store", dest = "gravity",
    type = int,
    help = "Sets or removes gravity; 0 = Rational mode, 1 = Default time pressure")

  parser.add_argument( '-id', '--SID',
    action = "store", dest = "SID",
    type = str,
    help = "Set subject ID.")

  parser.add_argument( '-ec', '--ECID',
    action = "store", dest = "ECID",
    type = str,
    help = "Set experimental condition ID.")

  parser.add_argument( '-rin', '--RIN',
      action = "store", dest = "RIN",
      type = str,
      help = "Set subject RIN.")

  #output stats to terminal; non-invasive
  parser.add_argument( '--stats',
    action = "store_true", dest = "boardstats",
    help = "Show board optimality metrics" )

  args = parser.parse_args()

  if args.self_test:
    from selftest import run
    return run()
  initialize_pygame()
  if args.config is None:
    fullscreen = cnf.default_fullscreen() if args.fullscreen is None else args.fullscreen
    args.config = configselect.choose(fullscreen=fullscreen)
    if args.config is None:
      pygame.quit()
      return
  pygame.mouse.set_visible(False)
  w = World( args )
  w.run()

if __name__ == '__main__':
  sys.exit(main())
