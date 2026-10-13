import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import cnf
import paths


def run():
  os.environ["SDL_VIDEODRIVER"] = "dummy"
  os.environ["SDL_AUDIODRIVER"] = "dummy"
  from tests import test_configs, test_text_input
  with tempfile.TemporaryDirectory() as directory:
    config_dir = Path(directory) / "configs"
    paths.initialize_configs(config_dir)
    with patch.object(cnf, "CONFIG_DIR", str(config_dir)):
      suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(module)
                                 for module in (test_configs, test_text_input))
      result = unittest.TextTestRunner(verbosity=2).run(suite)
  return 0 if result.wasSuccessful() else 1
