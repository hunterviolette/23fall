@echo off

:: Check if the Docker daemon is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
  echo Docker daemon is not running. Starting Docker...
  start docker
)

:: git pull
:: git checkout -b photo_lab
docker build -t photo_lab_image .
docker run -p 8050:8050 -it --rm photo_lab_image
start "" "http://localhost:8050/"
pause
