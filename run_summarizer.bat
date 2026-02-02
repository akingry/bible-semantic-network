@echo off
title Bible Summarizer - NASB
echo.
echo ========================================
echo   Bible Chapter Summarizer
echo   Using LM Studio + Llama 3.1 8B
echo ========================================
echo.
echo Make sure LM Studio is running with your model loaded!
echo.
pause

cd /d "%~dp0"
python bible_summarizer.py nasb.txt bible_summaries.json

echo.
echo ========================================
echo   Process complete!
echo ========================================
pause
