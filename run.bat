@echo off
docker info >nul 2>&1
if %errorlevel% neq 0 (
  echo Docker daemon is not running. Starting Docker...
  start docker
)

if %errorlevel% neq 0 (
  echo Failed to start docker, please start docker manually
)

docker build -t photo_lab_image .
docker run -p 8050:8050 -it --rm --name photo_lab photo_lab_image
echo Deleting docker container
pause