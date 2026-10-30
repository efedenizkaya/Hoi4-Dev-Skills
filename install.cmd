@echo off
rem Convenience wrapper: install.cmd [agent]
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
