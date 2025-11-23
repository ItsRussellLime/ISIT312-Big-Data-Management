@echo off
REM Windows Batch Script to Extract PDF Text
echo Starting PDF text extraction...
echo.

cd /d "G:\School\ISIT312\Exam_prep"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install PyPDF2 if needed
echo Installing PyPDF2...
python -m pip install PyPDF2 --quiet --disable-pip-version-check

REM Run the extraction script
echo.
echo Running extraction script...
python extract_all_pdfs.py

echo.
echo Extraction complete!
pause
