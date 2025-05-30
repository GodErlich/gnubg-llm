@echo off
echo Building gnubg container (only needed once or when Dockerfile changes)...
docker build -t gnubg-app .
echo.
echo Container built! Now you can use dev_run.bat for development.