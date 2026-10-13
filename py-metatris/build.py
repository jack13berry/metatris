import argparse
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def main():
  source = Path(__file__).resolve().parent
  target = platform.system().lower() + "-" + platform.machine().lower()
  parser = argparse.ArgumentParser(description="Build a single-file Metatris executable for this OS.")
  parser.add_argument("--output-dir", type=Path, default=source / "dist" / target)
  args = parser.parse_args()
  output = args.output_dir.resolve()
  work = source / "build" / target
  assets = work / "assets"
  assets.mkdir(parents=True, exist_ok=True)
  command = [sys.executable, "-m", "PyInstaller", "--onefile", "--console",
             "--noconfirm", "--clean", "--name", "metatris",
             "--distpath", str(output), "--workpath", str(work / "pyinstaller"),
             "--specpath", str(work), "--paths", str(source)]
  for directory in ("boards", "configs", "controllers", "media"):
    staged = assets / directory
    shutil.copytree(source / directory, staged, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("user.config", "__pycache__"))
    command.extend(["--add-data", str(staged) + ":" + directory])
  if sys.platform == "win32":
    command.extend(["--icon", str(source / "media" / "metatris.ico")])
  command.append(str(source / "main.py"))
  subprocess.run(command, cwd=source, check=True)
  executable = output / ("metatris.exe" if sys.platform == "win32" else "metatris")
  print("Built:", executable)


if __name__ == "__main__":
  main()
