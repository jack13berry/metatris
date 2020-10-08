import pygame, platform, time, numpy

import states, gui
import introscreen, playscreen

get_time = time.time if platform.system() == 'Windows' else time.process_time

#pre-renders reusable block surfaces
def generate_block( self, size, lvl, type ):
  if self.color_mode == "STANDARD":
    bg = pygame.Surface( ( size, size ) )
    c = self.STANDARD_colors[type]
    lvl_offset = lvl * 15
    bg_off = -40 + lvl_offset
    fg_off = 40 - lvl_offset
    bgc = tuple([min(max(a + b,0),255) for a, b in zip(c, [bg_off]*3)])
    fgc = tuple([min(max(a + b,0),255) for a, b in zip(c, [fg_off]*3)])
    bg.fill( bgc )
    fg = pygame.Surface( ( size - self.border * 2, size - self.border * 2 ) )
    fg.fill( fgc )
    fgr = fg.get_rect()
    fgr.topleft = ( self.border, self.border )
    bg.blit( fg, fgr )
  else:
    if type == 0:
      bgc = self.NES_colors[lvl][0]
      fgc = ( 255, 255, 255 )
    elif type == 1:
      #if self.color_mode == "other":
        #bgc = self.NES_colors[lvl][0]
        #fgc = self.NES_colors[lvl][0]
      if self.color_mode == "REMIX":
        bgc = self.NES_colors[lvl][1]
        fgc = self.NES_colors[lvl][0]
    elif type == 2:
      #if self.color_mode == "other":
        #bgc = self.NES_colors[lvl][1]
        #fgc = self.NES_colors[lvl][1]
      if self.color_mode == "REMIX":
        bgc = self.NES_colors[lvl][0]
        fgc = self.NES_colors[lvl][1]
    bg = pygame.Surface( ( size, size ) )
    bg.fill( bgc )
    fg = pygame.Surface( ( size - self.border * 2, size - self.border * 2 ) )
    fg.fill( fgc )
    fgr = fg.get_rect()
    fgr.topleft = ( self.border, self.border )
    bg.blit( fg, fgr )
    """
    if self.color_mode == "other":
      sheen = self.border - 1
      s1 = pygame.Surface( ( sheen, sheen ) )
      s1.fill( ( 255, 255, 255 ) )
      s1r = s1.get_rect()
      s2 = pygame.Surface( ( 2 * sheen, sheen ) )
      s2.fill( ( 255, 255, 255 ) )
      s2r = s2.get_rect()
      bg.blit( s1, ( s1r.left + 1, s1r.top + 1 ) )
      bg.blit( s2, ( s2r.left + 1 + sheen, s2r.top + 1 + sheen ) )
      bg.blit( s1, ( s1r.left + 1 + sheen, s1r.top + 1 + 2 * sheen ) )
    """
    if self.color_mode == "REMIX":
      sheen = self.border
      s = pygame.Surface( ( sheen,sheen ) )
      s.fill( ( 255, 255, 255 ) )
      sr = s.get_rect()
      sr.topleft = fgr.topleft
      bg.blit( s, sr.topleft )
  pygame.draw.rect( bg, self.bg_color, bg.get_rect(), 1 )
  return bg


#main draw updater
def drawTheWorld( self ):
  if self.state == states.Intro:
    introscreen.draw(self)
  elif self.state == states.Play:
    self.bg_color = self.tetris_flash_colors[self.tetris_flash_tick % 2]
    if self.tetris_flash_tick > 0:
      self.tetris_flash_tick -= 1
    self.gamesurf.fill( self.bg_color )
    playscreen.draw(self)
  elif self.state == states.Pause:
    self.worldsurf.fill( ( 0, 0, 0 ) )
    playscreen.drawPaused(self)
  elif self.state == states.Gameover:
    playscreen.drawGameOver(self)
  elif self.state == states.Aar:
    playscreen.draw_AAR(self)

  self.screen.blit( self.worldsurf, self.worldsurf_rect )
  pygame.display.flip()
