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
    self.world = SimpleNamespace(state=states.Intro, focused="intro.id",
                                 JOY_A=1, JOY_B=0, running=True,
                                 participant_id="", session_started=False, intro_message="",
                                 sounds={"uiaction": Mock()})
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
    self.assertEqual(self.world.participant_id, "")

  def test_id_accepts_shifted_underscore_dash_uppercase_and_backspace(self):
    self.press(pygame.K_a, "A", pygame.KMOD_SHIFT)
    self.press(pygame.K_MINUS, "_", pygame.KMOD_SHIFT)
    self.press(pygame.K_b, "b")
    self.press(pygame.K_MINUS, "-")
    self.press(pygame.K_2, "2")
    self.assertEqual(self.world.participant_id, "A_b-2")
    self.press(pygame.K_BACKSPACE, "\b")
    self.assertEqual(self.world.participant_id, "A_b-")

  def test_id_length_is_limited(self):
    for _ in range(introscreen.MAX_ID_LENGTH + 5):
      self.press(pygame.K_x, "x")
    self.assertEqual(len(self.world.participant_id), introscreen.MAX_ID_LENGTH)

  def test_typing_and_releasing_game_keys_only_changes_the_id(self):
    for key, text in ((pygame.K_i, "i"), (pygame.K_j, "j"),
                      (pygame.K_k, "k"), (pygame.K_p, "p")):
      self.press(key, text)
      self.press(key, event_type=pygame.KEYUP)
    self.assertEqual(self.world.participant_id, "ijkp")
    self.assertEqual(self.world.state, states.Intro)
    self.assertTrue(self.world.running)

  def test_unsupported_text_does_not_trigger_menu_actions(self):
    self.assertEqual(self.press(pygame.K_SPACE, " "), [])
    self.assertEqual(self.press(pygame.K_SLASH, "/"), [])
    self.assertTrue(self.world.running)
    self.assertEqual(self.world.participant_id, "")

  def test_ctrl_v_cmd_v_and_shift_insert_paste_the_clipboard(self):
    for key, mod in ((pygame.K_v, pygame.KMOD_LCTRL), (pygame.K_v, pygame.KMOD_RMETA),
                     (pygame.K_INSERT, pygame.KMOD_LSHIFT)):
      with self.subTest(key=key, mod=mod):
        self.world.participant_id = ""
        with patch.object(introscreen, "read_clipboard", return_value="P-12"):
          self.assertEqual(self.press(key, "\x16", mod), [events.keyPaste])
        self.assertEqual(self.world.participant_id, "P-12")
    # Plain v still types a letter.
    self.press(pygame.K_v, "v")
    self.assertEqual(self.world.participant_id, "P-12v")

  def test_paste_trims_whitespace_and_drops_characters_not_allowed(self):
    introscreen.paste(self.world, "  P-12\n")
    self.assertEqual((self.world.participant_id, self.world.intro_message), ("P-12", ""))
    self.world.participant_id = ""
    introscreen.paste(self.world, "P 12/a")
    self.assertEqual(self.world.participant_id, "P12a")
    self.assertTrue(self.world.intro_message)
    self.world.participant_id = ""
    introscreen.paste(self.world, "   ")
    self.assertEqual(self.world.participant_id, "")
    self.assertTrue(self.world.intro_message)

  def test_paste_respects_the_length_limit_and_a_started_session(self):
    self.world.participant_id = "x" * (introscreen.MAX_ID_LENGTH - 2)
    introscreen.paste(self.world, "abcd")
    self.assertEqual(self.world.participant_id, "x" * (introscreen.MAX_ID_LENGTH - 2) + "ab")
    self.assertTrue(self.world.intro_message)
    self.world.session_started = True
    with patch.object(introscreen, "read_clipboard", return_value="zz"):
      self.press(pygame.K_v, "\x16", pygame.KMOD_LCTRL)
    self.assertEqual(len(self.world.participant_id), introscreen.MAX_ID_LENGTH)

  def test_enter_submits_and_escape_quits_while_typing(self):
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
