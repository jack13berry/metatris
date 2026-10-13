import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame

import events
import introscreen
import states


class TextInputTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    pygame.init()

  @classmethod
  def tearDownClass(cls):
    pygame.quit()

  def setUp(self):
    self.world = SimpleNamespace(state=states.Intro, focused="signin.username",
                                 JOY_A=1, JOY_B=0, running=True,
                                 sounds={"uiaction": Mock()})
    for name, value in (("username_text", ""), ("password_text", ""),
                        ("email_text", ""), ("signin_screen", True)):
      self.enterContext(patch.object(introscreen, name, value))
    with patch.object(events, "setupControllers"):
      events.init(self.world)
    pygame.event.clear()

  def press(self, key, text="", mod=0, event_type=pygame.KEYDOWN):
    pygame.event.post(pygame.event.Event(event_type, key=key, unicode=text, mod=mod))
    mapped = events.readAll(self.world)
    for event in mapped:
      introscreen.handleInput(self.world, event)
    return mapped

  def test_shift_alone_does_not_insert_text(self):
    for key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
      with self.subTest(key=key):
        self.assertEqual(self.press(key, mod=pygame.KMOD_SHIFT), [])
        self.assertEqual(self.press(key, event_type=pygame.KEYUP), [])
    self.assertEqual(introscreen.username_text, "")

  def test_username_accepts_shifted_underscore_and_uppercase(self):
    for signing_in in (True, False):
      with self.subTest(signing_in=signing_in):
        introscreen.signin_screen = signing_in
        introscreen.username_text = ""
        self.press(pygame.K_a, "A", pygame.KMOD_SHIFT)
        self.press(pygame.K_MINUS, "_", pygame.KMOD_SHIFT)
        self.press(pygame.K_b, "b")
        self.press(pygame.K_2, "2")
        self.assertEqual(introscreen.username_text, "A_b2")
        self.press(pygame.K_BACKSPACE, "\b")
        self.assertEqual(introscreen.username_text, "A_b")

  def test_at_sign_comes_from_the_typed_character(self):
    self.world.focused = "register.email"
    self.press(pygame.K_RSHIFT, mod=pygame.KMOD_RSHIFT)
    self.press(pygame.K_2, "@", pygame.KMOD_RSHIFT)
    self.press(pygame.K_PERIOD, ".")
    self.press(pygame.K_2, "2")
    self.assertEqual(introscreen.email_text, "@.2")
    self.assertEqual(introscreen.username_text, "")

  def test_password_preserves_shifted_characters(self):
    self.world.focused = "signin.pw"
    self.press(pygame.K_a, "A", pygame.KMOD_SHIFT)
    self.press(pygame.K_MINUS, "_", pygame.KMOD_SHIFT)
    self.assertEqual(introscreen.password_text, "A_")

  def test_typing_and_releasing_game_keys_only_changes_the_field(self):
    for key, text in ((pygame.K_i, "i"), (pygame.K_j, "j"),
                      (pygame.K_k, "k"), (pygame.K_p, "p")):
      self.press(key, text)
      self.press(key, event_type=pygame.KEYUP)
    self.assertEqual(introscreen.username_text, "ijkp")
    self.assertEqual(self.world.state, states.Intro)
    self.assertTrue(self.world.running)

  def test_unsupported_text_does_not_trigger_menu_actions(self):
    self.assertEqual(self.press(pygame.K_SPACE, " "), [])
    self.assertEqual(self.press(pygame.K_MINUS, "-"), [])
    self.assertTrue(self.world.running)
    self.assertEqual(introscreen.username_text, "")

  def test_navigation_and_submit_work_while_a_field_is_focused(self):
    self.assertEqual(events.map(self.world, pygame.event.Event(pygame.KEYDOWN,
      key=pygame.K_UP, unicode="")), events.btnUpOn)
    with patch.object(introscreen, "moveForward") as submit:
      self.press(pygame.K_RETURN, "\r")
      submit.assert_called_once_with(self.world)
    self.press(pygame.K_ESCAPE, "\x1b")
    self.assertFalse(self.world.running)

  def test_text_mapping_does_not_override_game_controls(self):
    self.world.state = states.Play
    for key, text, action in ((pygame.K_j, "j", events.btnRotateCwOn),
                              (pygame.K_k, "k", events.btnRotateCcwOn),
                              (pygame.K_p, "p", events.reqPauseResume),
                              (pygame.K_i, "i", events.reqScreenShot)):
      with self.subTest(key=key):
        self.assertEqual(events.map(self.world, pygame.event.Event(pygame.KEYDOWN,
          key=key, unicode=text)), action)


if __name__ == "__main__":
  unittest.main()
