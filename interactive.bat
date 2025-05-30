@echo off
echo Starting interactive gnubg session...
docker run -it --rm ^
    -v %cd%\output:/app/output ^
    -v %cd%\input:/app/input ^
    -v %cd%\llm_version.py:/app/llm_version.py ^
    -v %cd%\.env:/app/.env ^
    gnubg-app gnubg -t
