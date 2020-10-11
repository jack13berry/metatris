import pygame

import gui

#draw the introduction screen
def draw( self ):
  self.worldsurf.fill( ( 39, 39, 39 ) )
  logo_rect = self.logo.get_rect()
  logo_rect.centerx = self.worldsurf_rect.centerx
  logo_rect.top = 50
  self.worldsurf.blit( self.logo, logo_rect )

  gclogo_rect = self.gclogo.get_rect()
  gclogo_rect.bottom = self.worldsurf_rect.bottom - 20
  gclogo_rect.centerx = self.worldsurf_rect.centerx
  self.worldsurf.blit( self.gclogo, gclogo_rect )

  self.title_blink_timer += 1

  if self.title_blink_timer <= self.fps:
    if pygame.joystick.get_count() > 0:
      gui.textSurface(self, "press START to begin", self.scores_font, ( 200, 200, 200 ), ( self.worldsurf_rect.centerx, self.worldsurf_rect.height - self.worldsurf_rect.height / 5 ), self.worldsurf )
    else:
      gui.textSurface(self, "press SPACE BAR to begin", self.scores_font, ( 200, 200, 200 ), ( self.worldsurf_rect.centerx, self.worldsurf_rect.height - self.worldsurf_rect.height / 5 ), self.worldsurf )

  if self.title_blink_timer > self.fps * 2:
      self.title_blink_timer = 0
