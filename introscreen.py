import pygame

import gui

#draw the introduction screen
def draw( self ):
  self.worldsurf.fill( ( 39, 39, 39 ) )
  logo_rect = self.logo.get_rect()
  logo_rect.centerx = self.worldsurf_rect.centerx
  logo_rect.top = 50
  self.worldsurf.blit( self.logo, logo_rect )

  cwl_rect = self.cw_logo.get_rect()
  #cwl_rect.left = logo_rect.left
  #cwl_rect.top = logo_rect.top + logo_rect.height * 2 / 3
  cwl_rect.bottom = self.worldsurf_rect.bottom - 20
  cwl_rect.left = logo_rect.left
  self.worldsurf.blit( self.cw_logo, cwl_rect )

  rpi_rect = self.rpi_seal.get_rect()
  #rpi_rect.left = logo_rect.left + logo_rect.width * 3 / 4
  #rpi_rect.top = logo_rect.top + logo_rect.height * 2 / 3
  rpi_rect.bottom = self.worldsurf_rect.bottom - 20
  rpi_rect.right = logo_rect.right
  self.worldsurf.blit( self.rpi_seal, rpi_rect )


  self.title_blink_timer += 1

  if self.title_blink_timer <= self.fps * 3 / 4:
    if pygame.joystick.get_count() > 0:
      gui.textSurface(self, "press START to begin", self.scores_font, ( 200, 200, 200 ), ( self.worldsurf_rect.centerx, self.worldsurf_rect.height - self.worldsurf_rect.height / 5 ), self.worldsurf )
    else:
      gui.textSurface(self, "press SPACE BAR to begin", self.scores_font, ( 200, 200, 200 ), ( self.worldsurf_rect.centerx, self.worldsurf_rect.height - self.worldsurf_rect.height / 5 ), self.worldsurf )
  if self.title_blink_timer >= self.fps * 3 / 2:
      self.title_blink_timer = 0
