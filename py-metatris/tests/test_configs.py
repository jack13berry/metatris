import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
GAME_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GAME_DIR))

import pygame

import cnf
import configselect
import events
import inputhandler
import logger
import paths
import playscreen
import states
from world import World
from zoid import Zoid
from simulator import TetrisSimulator


class SimulatorFeatureTests(unittest.TestCase):
  def hole_board(self):
    board = [[0] * 10 for _ in range(20)]
    for row in (16, 18, 19):
      board[row][0] = 1
    return board

  def test_holes_depth_and_column_transitions_survive_height_calculation(self):
    sim = TetrisSimulator(board=self.hole_board())
    features = sim.report_board_features()
    self.assertEqual(features["max_ht"], 4)
    self.assertEqual(features["pits"], 1)
    self.assertEqual(features["pit_rows"], 1)
    self.assertEqual(features["lumped_pits"], 1)
    self.assertEqual(features["pit_depth"], 1)
    self.assertEqual(features["mean_pit_depth"], 1)
    self.assertEqual(features["col_trans"], 3)
    self.assertEqual(features["pattern_div"], 2)

  def test_hole_change_uses_the_previous_board(self):
    previous = [[0] * 10 for _ in range(20)]
    previous[-1][0] = 1
    sim = TetrisSimulator(board=self.hole_board())
    features = sim.get_features(sim.space, prev_space=previous)
    self.assertEqual(features["d_pits"], 1)
    self.assertEqual(features["d_max_ht"], 3)

  def test_column_diversity_counts_unique_adjacent_patterns(self):
    sim = TetrisSimulator()
    columns = [(0, 0), (0, 1), (0, 0), (0, 1), (0, 1)]
    with contextlib.redirect_stdout(io.StringIO()) as output:
      self.assertEqual(sim.get_col_diversity(columns), 3)
      self.assertEqual(sim.get_col_diversity([(0, 0)] * 10), 1)
      self.assertEqual(sim.get_col_diversity([]), 0)
    self.assertEqual(output.getvalue(), "")

  def test_features_use_board_after_line_clearing(self):
    board = [[0] * 10 for _ in range(20)]
    for row in (15, 17, 18):
      board[row][0] = 1
    board[-1] = [1] * 10
    features = TetrisSimulator(board=board).report_board_features()
    self.assertEqual(features["cleared"], 1)
    self.assertEqual(features["full_cells"], 3)
    self.assertEqual(features["max_ht"], 4)
    self.assertEqual(features["pits"], 1)
    self.assertEqual(features["col_trans"], 3)

  def test_controller_uses_actual_holes_in_candidate_boards(self):
    board = [[0] * 10 for _ in range(20)]
    board[-1][:4] = [1] * 4
    board[-2][1] = 1
    for overhangs in (False, True):
      with self.subTest(overhangs=overhangs):
        sim = TetrisSimulator(board=board, curr="T", controller={"pits": -1},
                              overhangs=overhangs)
        chosen = sim.predict(board, "T")
        hole_counts = []
        for option in sim.options:
          remaining = [row for row in option[3] if not all(row)]
          holes = 0
          for column in zip(*remaining):
            occupied_above = False
            for cell in column:
              if cell:
                occupied_above = True
              elif occupied_above:
                holes += 1
          self.assertEqual(option[4]["pits"], holes)
          hole_counts.append(holes)
        self.assertGreater(max(hole_counts), min(hole_counts))
        self.assertEqual(chosen[4]["pits"], min(hole_counts))


class ConfigTests(unittest.TestCase):
  def setUp(self):
    directory = self.enterContext(tempfile.TemporaryDirectory())
    self.directory = Path(directory)
    self.enterContext(patch.object(cnf, "CONFIG_DIR", directory))
    (self.directory / "default.config").write_text(
      'starting_level = 1\nrender_scores = False\nfixed_seeds = False\n'
      'game_type = "standard"\nscoring = 40, 100, 300, 1200, 6000\n')

  def load(self, name="default"):
    world = SimpleNamespace(startTime=1.0)
    cnf.load(world, name)
    return world

  def test_discovery_includes_new_profiles_and_sorts_default_first(self):
    for name in ("zeta.config", "alpha.config", "user.config", "notes.md"):
      (self.directory / name).write_text("")
    (self.directory / "folder.config").mkdir()
    self.assertEqual(cnf.available_configs(), ["default", "alpha", "user", "zeta"])
    (self.directory / "new.config").write_text("")
    self.assertIn("new", cnf.available_configs())

  def test_override_inherits_defaults_and_parses_inline_comments(self):
    (self.directory / "study.config").write_text(
      'starting_level = 0 # slower\nrender_scores = True\n'
      'game_type = "condition=one"\nrandom_seeds = 12, 34\nfixed_seeds = True\n')
    world = self.load("study")
    self.assertEqual(world.scoring, [40, 100, 300, 1200, 6000])
    self.assertEqual(world.starting_level, 0)
    self.assertTrue(world.render_scores)
    self.assertEqual(world.game_type, "condition=one")
    self.assertEqual(world.random_seeds, [12, 34])
    self.assertTrue(world.fixed_seeds)
    self.assertEqual(world.config_name, "study")

  def test_default_and_study_are_not_overridden_by_saved_user_settings(self):
    (self.directory / "user.config").write_text("starting_level = 9\nhint_zoid = True\n")
    (self.directory / "study.config").write_text("starting_level = 0\n")
    self.assertEqual(self.load().starting_level, 1)
    self.assertFalse(self.load("study").hint_zoid)
    self.assertEqual(self.load("user").starting_level, 9)

  def test_reloading_removes_previous_overrides(self):
    (self.directory / "study.config").write_text("hint_zoid = True\n")
    world = self.load("study")
    cnf.load(world, "default")
    self.assertFalse(world.hint_zoid)
    self.assertEqual(len(world.configs_to_write), len(set(world.configs_to_write)))

  def test_explicit_false_fixed_seeds_is_respected(self):
    (self.directory / "random.config").write_text("random_seeds = 1, 2\nfixed_seeds = False\n")
    self.assertFalse(self.load("random").fixed_seeds)

  def test_bad_config_reports_source_and_line(self):
    (self.directory / "bad.config").write_text("# comment\ninvalid setting\n")
    with self.assertRaisesRegex(ValueError, r"bad.config:2"):
      self.load("bad")
    with self.assertRaises(FileNotFoundError):
      self.load("missing")

  def test_picker_navigation_controller_and_paging(self):
    for number in range(20):
      (self.directory / ("profile_%02d.config" % number)).write_text("")
    picker = configselect.ConfigPicker()
    self.assertEqual(picker.names[picker.index], "default")
    picker.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEDOWN))
    self.assertEqual(picker.index, 8)
    picker.handle_event(pygame.event.Event(pygame.JOYHATMOTION, value=(0, -1)))
    self.assertEqual(picker.index, 9)
    axis = pygame.event.Event(pygame.JOYAXISMOTION, joy=0, axis=1, value=1.0)
    picker.handle_event(axis)
    picker.handle_event(axis)
    self.assertEqual(picker.index, 10)
    choice = picker.handle_event(pygame.event.Event(pygame.JOYBUTTONDOWN, button=1))
    self.assertEqual(choice, picker.names[10])
    self.assertFalse(picker.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)))

  def test_picker_usb_gamepad_b_exits(self):
    picker = configselect.ConfigPicker()
    self.assertIs(picker.handle_event(pygame.event.Event(pygame.JOYBUTTONDOWN, button=2)), False)


class StudyProfileTests(unittest.TestCase):
  def test_study_profiles_have_common_settings_and_distinct_aids(self):
    durations = {"practice": 90, "baseline": 300, "acq_normal": 1800,
                 "acq_bar": 1800, "acq_cue": 1800, "acq_prescriptive": 1800, "test": 600}
    seed_sets = {}
    for name, duration in durations.items():
      with self.subTest(name=name):
        world = SimpleNamespace(startTime=1.0)
        cnf.load(world, name)
        self.assertEqual(world.game_type, name)
        self.assertEqual(world.time_limit, duration)
        self.assertEqual(world.starting_level, 0)
        self.assertEqual(world.continues, 0)
        self.assertTrue(world.render_scores)
        self.assertTrue(world.fixed_seeds)
        self.assertFalse(world.permute_seeds)
        for setting in ("hint_button", "ghost_zoid", "AAR", "solve_button", "auto_solve", "spotlight"):
          self.assertFalse(getattr(world, setting), setting)
        self.assertEqual(world.bar, name == "acq_bar")
        self.assertEqual(world.hint_context, name == "acq_cue")
        self.assertEqual(world.hint_zoid, name == "acq_prescriptive")
        if name in ("acq_cue", "acq_prescriptive"):
          self.assertEqual(world.controller, "score_506_dellacherie")
          self.assertFalse(world.sim_overhangs)
        seed_sets[name] = world.random_seeds
    for name in ("acq_bar", "acq_cue", "acq_prescriptive"):
      self.assertEqual(seed_sets[name], seed_sets["acq_normal"])
    distinct = [set(seed_sets[name]) for name in ("practice", "baseline", "acq_normal", "test")]
    for index, seeds in enumerate(distinct):
      for other in distinct[index + 1:]:
        self.assertTrue(seeds.isdisjoint(other))


class PortablePathTests(unittest.TestCase):
  def test_game_can_start_without_an_audio_device(self):
    import main
    with patch("main.pygame.init"), patch("main.pygame.mixer.quit") as quit_mixer, \
         patch("main.pygame.mixer.init", side_effect=[pygame.error("No audio device"), None]) as init_mixer, \
         patch.dict(os.environ):
      main.initialize_pygame()
      self.assertEqual(os.environ["SDL_AUDIODRIVER"], "dummy")
      self.assertEqual(init_mixer.call_count, 2)
      quit_mixer.assert_called_once()

  def test_initial_configs_are_copied_without_overwriting_edits(self):
    with tempfile.TemporaryDirectory() as directory:
      config_dir = Path(directory) / "configs"
      paths.initialize_configs(config_dir)
      self.assertTrue((config_dir / "baseline.config").is_file())
      (config_dir / "baseline.config").write_text("starting_level = 5\n")
      paths.initialize_configs(config_dir)
      self.assertEqual((config_dir / "baseline.config").read_text(), "starting_level = 5\n")

  def test_relative_data_directory_uses_app_home(self):
    with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"METATRIS_HOME": directory}):
      self.assertEqual(paths.writable_path("data"), str(Path(directory) / "data"))
      absolute = str(Path(directory) / "custom_logs")
      self.assertEqual(paths.writable_path(absolute), absolute)


class GameConfigIntegrationTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.previous_directory = os.getcwd()
    os.chdir(GAME_DIR)
    pygame.init()

  @classmethod
  def tearDownClass(cls):
    pygame.quit()
    os.chdir(cls.previous_directory)

  def setUp(self):
    self.enterContext(contextlib.redirect_stdout(io.StringIO()))
    self.enterContext(patch("world.Thread"))
    self.enterContext(patch("logger.Thread"))
    self.enterContext(patch("world.time.sleep"))
    self.logdir = self.enterContext(tempfile.TemporaryDirectory())
    read_file = cnf.read_file
    def read_with_logdir(name):
      values = read_file(name)
      if name == "default":
        values["logdir"] = self.logdir
      return values
    self.enterContext(patch.object(cnf, "read_file", side_effect=read_with_logdir))

  def make_world(self, profile="baseline", session="test"):
    world = World(argparse.Namespace(config=profile, logfile=session, boardstats=False))
    self.addCleanup(world.quit)
    return world

  def start_game(self, world):
    world.state = states.Setup
    world.process_game_logic()
    world.moment += 1
    world.process_game_logic()

  def test_all_profiles_initialize_and_use_the_selected_simulator(self):
    for name in cnf.available_configs():
      with self.subTest(name=name):
        world = self.make_world(name, session=name)
        self.start_game(world)
        playscreen.draw(world)
        self.assertEqual(world.config_name, name)
        self.assertEqual(world.sim.overhangs, world.sim_overhangs)
        self.assertEqual(world.sim.controller, world.get_controller())
        self.assertEqual(world.hint_toggle, world.hint_zoid)

  def test_assets_load_from_an_unrelated_working_directory(self):
    previous = os.getcwd()
    with tempfile.TemporaryDirectory() as directory:
      try:
        os.chdir(directory)
        world = self.make_world("acq_prescriptive")
        self.start_game(world)
        playscreen.draw(world)
        self.assertTrue(world.solved)
      finally:
        os.chdir(previous)

  def test_command_line_settings_override_the_selected_profile(self):
    world = SimpleNamespace(startTime=1.0, args=argparse.Namespace(
      config="baseline", SID="Participant_42", logdir=self.logdir, gravity=1,
      logfile="test", boardstats=False, self_test=False))
    cnf.load(world, "baseline")
    self.assertEqual(world.SID, "Participant_42")
    self.assertEqual(world.logdir, self.logdir)
    self.assertTrue(world.gravity)

  def test_controller_a_rotates_clockwise_and_b_counterclockwise(self):
    world = self.make_world()
    self.start_game(world)
    events.init(world)
    world.curr_zoid = Zoid("T", world)
    a_event = events.map(world, pygame.event.Event(pygame.JOYBUTTONDOWN, button=world.JOY_A))
    b_event = events.map(world, pygame.event.Event(pygame.JOYBUTTONDOWN, button=world.JOY_B))
    self.assertEqual(a_event, events.btnRotateCwOn)
    self.assertEqual(b_event, events.btnRotateCcwOn)
    inputhandler.playStateHandler(world, a_event)
    self.assertEqual(world.curr_zoid.rot, 1)
    inputhandler.playStateHandler(world, b_event)
    self.assertEqual(world.curr_zoid.rot, 0)
    self.assertEqual(events.mappedBtnNames["Rotate CW"], "A")
    self.assertEqual(events.mappedBtnNames["Rotate CCW"], "B")

    for piece_type in ("T", "J", "L"):
      world.curr_zoid = piece = Zoid(piece_type, world)
      piece.row = 15
      for rotation in range(piece.rots):
        for event, direction in ((a_event, 1), (b_event, -1)):
          with self.subTest(piece=piece_type, rotation=rotation, direction=direction):
            piece.rot = rotation
            shape = piece.get_shape()
            expected = ([list(column) for column in zip(*shape[::-1])] if direction == 1
                        else [list(column) for column in zip(*shape)][::-1])
            inputhandler.playStateHandler(world, event)
            self.assertEqual(piece.get_shape(), expected)
            self.assertEqual((piece.col, piece.row), (3, 15))

  def test_controller_b_rotates_once_per_press_and_wraps_around(self):
    world = self.make_world()
    self.start_game(world)
    events.init(world)
    pygame.event.clear()
    for piece_type in Zoid.set_tetris:
      world.curr_zoid = piece = Zoid(piece_type, world)
      piece.row = 15
      world.rots = 0
      for expected_rotation in range(piece.rots - 1, -1, -1):
        with self.subTest(piece=piece_type, rotation=expected_rotation):
          for event_type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
            pygame.event.post(pygame.event.Event(event_type, button=world.JOY_B))
          for event in events.readAll(world):
            inputhandler.playStateHandler(world, event)
          self.assertEqual(piece.rot, expected_rotation)
      self.assertEqual(world.rots, piece.rots)

  def test_usb_gamepad_b_rotates_the_reported_l_piece_counterclockwise(self):
    world = self.make_world()
    self.start_game(world)
    events.init(world)
    world.curr_zoid = piece = Zoid("L", world)
    piece.row, piece.rot = 15, 1
    initial_shape = piece.get_shape()
    self.assertEqual(initial_shape, [[7, 7, 0], [0, 7, 0], [0, 7, 0]])

    for event_type, expected_event in ((pygame.JOYBUTTONDOWN, events.btnRotateCcwOn),
                                        (pygame.JOYBUTTONUP, events.btnRotateCcwOff)):
      event = events.map(world, pygame.event.Event(event_type, button=2))
      self.assertEqual(event, expected_event)
      inputhandler.playStateHandler(world, event)
    self.assertEqual(piece.get_shape(), [[0, 0, 0], [7, 7, 7], [7, 0, 0]])
    self.assertEqual(piece.rot, 0)
    self.assertEqual(world.rots, 1)

    a_event = events.map(world, pygame.event.Event(pygame.JOYBUTTONDOWN, button=1))
    inputhandler.playStateHandler(world, a_event)
    self.assertEqual(piece.get_shape(), initial_shape)

  def test_controller_b_kicks_away_from_walls_and_stacked_blocks(self):
    world = self.make_world()
    self.start_game(world)
    events.init(world)
    b_event = events.map(world, pygame.event.Event(pygame.JOYBUTTONDOWN, button=world.JOY_B))
    for rotation, column, expected_column in ((3, -1, 0), (1, 8, 7), (0, 3, 2)):
      with self.subTest(rotation=rotation, column=column):
        world.board = [[0] * world.game_wd for _ in range(world.game_ht)]
        if rotation == 0:
          world.board[5][4] = 1
        world.curr_zoid = piece = Zoid("T", world)
        piece.rot, piece.col, piece.row = rotation, column, 15
        self.assertFalse(piece.collide(piece.col, piece.row, piece.rot, world.board))
        inputhandler.playStateHandler(world, b_event)
        self.assertEqual(piece.rot, (rotation - 1) % piece.rots)
        self.assertEqual((piece.col, piece.row), (expected_column, 15))
        self.assertFalse(piece.collide(piece.col, piece.row, piece.rot, world.board))

  def test_controller_b_preserves_the_piece_when_rotation_is_blocked(self):
    world = self.make_world()
    self.start_game(world)
    events.init(world)
    world.board[5][3:6] = [1, 1, 1]
    world.curr_zoid = piece = Zoid("T", world)
    piece.row = 15
    self.assertFalse(piece.collide(piece.col, piece.row, piece.rot, world.board))
    b_event = events.map(world, pygame.event.Event(pygame.JOYBUTTONDOWN, button=world.JOY_B))
    inputhandler.playStateHandler(world, b_event)
    self.assertEqual((piece.rot, piece.col, piece.row), (0, 3, 15))

  def test_unlimited_continues_preserve_block_timer_and_advance_seeds(self):
    world = self.make_world()
    self.start_game(world)
    start = world.blockStartTime
    self.assertEqual(world.seeds_used, ["2101"])
    world.game_over()
    world.gameover_anim_tick = world.gameover_tick_max + 1
    world.input_continue()
    self.assertEqual(world.state, states.Setup)
    world.moment += 5
    world.process_game_logic()
    self.assertEqual(world.blockStartTime, start)
    self.assertEqual(world.seeds_used, ["2101", "2102"])
    world.moment = start + world.time_limit
    world.process_game_logic()
    self.assertTrue(world.time_limit_reached)
    self.assertFalse(world.game_active)
    self.assertEqual(world.state, states.Gameover)
    world.input_continue()
    self.assertEqual(world.state, states.Gameover)
    world.unifile.flush()
    rows = Path(world.unifile_path).read_text().splitlines()
    header = rows[0].split("\t")
    summaries = [row.split("\t") for row in rows[1:] if row.split("\t")[1] == "GAME_SUMM"]
    self.assertEqual(len(summaries), 2)
    self.assertEqual(summaries[-1][header.index("completed")], "False")

  def test_time_limit_includes_pause_but_not_initial_menu(self):
    world = self.make_world("practice")
    world.moment += 1000
    world.process_game_logic()
    self.assertFalse(world.time_limit_reached)
    self.start_game(world)
    world.state = states.Pause
    world.moment = world.blockStartTime + 90
    world.process_game_logic()
    self.assertTrue(world.time_limit_reached)
    self.assertEqual(world.state, states.Gameover)

  def test_saved_logs_snapshots_scores_and_performance_identify_config(self):
    world = self.make_world("acq_bar")
    self.start_game(world)
    while not world.curr_zoid.collide(world.curr_zoid.col, world.curr_zoid.row - 1,
                                      world.curr_zoid.rot, world.board):
      world.curr_zoid.down(0)
    world.curr_zoid.down(0)
    world.moment += 1
    logger.worldState(world)
    world.game_over()
    for file in (world.unifile, world.epfile, world.gamefile, world.scorefile):
      file.flush()
    for path in (world.unifile_path, world.epfile_path, world.gamefile_path, world.scorefile_path):
      rows = [line.split("\t") for line in Path(path).read_text().splitlines()]
      header = rows[0]
      self.assertIn("config_name", header)
      self.assertGreater(len(rows), 1)
      for row in rows[1:]:
        self.assertEqual(len(row), len(header))
        self.assertEqual(row[header.index("config_name")], "acq_bar")
        self.assertEqual(row[header.index("game_type")], "acq_bar")
    self.assertIn("config_name = acq_bar", Path(world.configfile_path).read_text())
    self.assertIn("config_name: acq_bar", Path(world.histfile_path).read_text())
    self.assertIn("Config: acq_bar", world.getperf())
    self.assertIn("Game type: acq_bar", world.getperf())

  def test_variable_length_logs_identify_config(self):
    world = self.make_world()
    self.start_game(world)
    world.fixed_log = False
    world.unifile.seek(0)
    world.unifile.truncate()
    logger.game_event(world, "TEST")
    logger.worldState(world)
    logger.episode(world)
    world.game_over()
    world.unifile.flush()
    rows = Path(world.unifile_path).read_text().splitlines()
    for row in rows:
      self.assertIn(":config_name\tbaseline", row)

  def test_saved_episode_records_real_holes_and_corrected_log_version(self):
    world = self.make_world("acq_bar")
    self.start_game(world)
    world.board = SimulatorFeatureTests().hole_board()
    world.curr_zoid = Zoid("O", world)
    while not world.curr_zoid.collide(world.curr_zoid.col, world.curr_zoid.row - 1,
                                      world.curr_zoid.rot, world.board):
      world.curr_zoid.row -= 1
    world.sim.set_board(world.board)
    world.sim.set_zoids("O", world.next_zoid.type)
    world.moment += 1
    logger.episode(world)
    world.unifile.flush()
    lines = Path(world.unifile_path).read_text().splitlines()
    header = lines[0].split("\t")
    rows = [dict(zip(header, line.split("\t"))) for line in lines[1:]]
    episode = next(row for row in rows if row["event_type"] == "EP_SUMM")
    self.assertEqual(episode["pits"], "1")
    self.assertGreater(float(episode["col_trans"]), 0)
    self.assertTrue(json.loads(episode["board_rep"].strip("'")))
    version = next(row for row in rows if row["evt_id"] == "LOG_VERSION")
    self.assertEqual(version["evt_data1"], "3.3")

  def test_only_lagging_bar_profile_renders_performance_feedback(self):
    normal = self.make_world("acq_normal", "normal")
    self.start_game(normal)
    playscreen.draw(normal)
    self.assertEqual(normal.worldsurf.get_at(normal.metabarBox.center)[:3], normal.bg_color)
    bar = self.make_world("acq_bar", "bar")
    self.start_game(bar)
    playscreen.draw(bar)
    self.assertNotEqual(bar.worldsurf.get_at(bar.metabarBox.center)[:3], bar.bg_color)

  def test_leading_outline_requires_recommended_column_and_rotation(self):
    world = self.make_world("acq_cue")
    self.start_game(world)
    world.curr_zoid.col = world.solved_col
    world.curr_zoid.rot = world.solved_rot
    with patch("playscreen.gui.blocks") as draw_blocks:
      playscreen.draw_curr_zoid(world)
      self.assertTrue(draw_blocks.call_args.kwargs["outline"])
      self.assertEqual(draw_blocks.call_count, 2)
      draw_blocks.reset_mock()
      world.curr_zoid.col += 1
      playscreen.draw_curr_zoid(world)
      self.assertEqual(draw_blocks.call_count, 1)
      draw_blocks.reset_mock()
      world.curr_zoid.col = world.solved_col
      world.curr_zoid.rot = (world.solved_rot + 1) % world.curr_zoid.rots
      playscreen.draw_curr_zoid(world)
      self.assertEqual(draw_blocks.call_count, 1)

  def test_prescriptive_outline_is_visible_before_moving_piece(self):
    world = self.make_world("acq_prescriptive")
    self.start_game(world)
    with patch("playscreen.gui.blocks") as draw_blocks:
      playscreen.draw_curr_zoid(world)
      self.assertTrue(draw_blocks.call_args.kwargs["outline"])
      self.assertEqual(draw_blocks.call_count, 2)


if __name__ == "__main__":
  unittest.main()
