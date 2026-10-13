import os
from pathlib import Path
import shutil
import sys


RESOURCE_DIR = Path(__file__).resolve().parent
FROZEN = getattr(sys, "frozen", False)
APP_DIR = Path(sys.executable).resolve().parent if FROZEN else RESOURCE_DIR


def resource(*parts):
  return str(RESOURCE_DIR.joinpath(*parts))


def user_directory():
  if sys.platform == "win32":
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
  elif sys.platform == "darwin":
    base = Path.home() / "Library" / "Application Support"
  else:
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
  return base / "metatris"


def app_directory():
  override = os.environ.get("METATRIS_HOME")
  if override:
    return Path(override).expanduser().resolve()
  return APP_DIR if os.access(APP_DIR, os.W_OK) else user_directory()


def initialize_configs(directory):
  directory = Path(directory)
  directory.mkdir(parents=True, exist_ok=True)
  for source in (RESOURCE_DIR / "configs").glob("*.config"):
    target = directory / source.name
    if source.name != "user.config" and not target.exists():
      shutil.copyfile(source, target)


def writable_path(path):
  path = Path(path).expanduser()
  return str(path if path.is_absolute() else app_directory() / path)
