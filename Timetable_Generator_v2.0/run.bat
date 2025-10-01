@echo off
REM --- SETTINGS ---
SET EXECUTABLE_PATH="./main.exe"
SET PYTHON_SCRIPT="./app.py"
SET PYTYHON_COMAND

echo Starting the executable...

REM The batch script will immediately move to the next line (the Python script).
start "" %EXECUTABLE_PATH%

echo.
echo Algo server started.
echo Running Python script: %PYTHON_SCRIPT%
echo.

REM Ensure 'python' is in your system's PATH.
REM You can use 'py' instead of 'python' on some Windows systems.
%PYTYHON_COMAND% %PYTHON_SCRIPT%

echo.
echo Script execution complete. Press any key to exit.
pause > nul