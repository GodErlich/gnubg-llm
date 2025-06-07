@echo off
echo Starting interactive gnubg session...
docker run -it --rm ^
    -v %cd%\output:/app/output ^
    -v %cd%\input:/app/input ^
    -v %cd%\main.py:/app/main.py ^
    -v %cd%\.env:/app/.env ^
    gnubg-app gnubg -t
