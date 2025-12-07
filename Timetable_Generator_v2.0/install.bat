@echo off
echo Installing required Python packages...

REM List of packages to install:
REM flask (for 'import flask as f')
REM csv (standard library, but sometimes helpful to include for completeness, though usually not needed)
REM requests
REM json (standard library, not needed for pip install)
REM sqlite3 (standard library, not needed for pip install)
REM webview
REM threading (standard library, not needed for pip install)
REM Other imports: io, os, which are standard library (not pip installable)

pip install flask requests
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: One or more package installations failed!
    echo Please ensure Python and pip are correctly installed and accessible in your system's PATH.
    echo.
) ELSE (
    echo.
    echo All specified packages installed successfully!
    echo.
)

pause