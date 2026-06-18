@echo off
cd /d "%~dp0"
"%~dp0venv\Scripts\pyside6-designer.exe" "%~dp0ui\main_window.ui"
