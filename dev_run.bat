@echo off
echo Running gnubg with live file changes (no rebuild needed)...
docker run -it --rm ^
    -v %cd%\output:/app/output ^
    -v %cd%\input:/app/input ^
    -v %cd%\llm_version.py:/app/llm_version.py ^
    -v %cd%\.env:/app/.env ^
    gnubg-app
