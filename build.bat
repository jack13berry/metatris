@echo off

python setup.py build
for %%a in (.\build\exe.*) do echo %%a

for /D /r %%P in ("build\exe.*") do (
  echo Will copy resources into build\%%~nxP
  for %%a in (boards configs controllers media) do (
    mkdir build\%%~nxP\%%a
    copy %%a\* build\%%~nxP\%%a\
  )
)
