@echo off

if exist dist (
  del /Q /S dist
  rmdir /Q /S dist
)

if exist build (
  del /Q /S build
  rmdir /Q /S build
)
