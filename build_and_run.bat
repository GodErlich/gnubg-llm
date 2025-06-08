@echo off
echo Building gnubg container...
docker build -t gnubg-app .
echo Cleaning up old images...
docker image prune -f
echo Running gnubg container...
docker run -it --rm ^
    -v %cd%\output:/app/output ^
    -v %cd%\input:/app/input ^
    gnubg-app