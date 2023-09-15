@echo off
docker info >nul 2>&1
if %errorlevel% neq 0 (
  echo Docker daemon is not running. Starting Docker...
  start docker
)

docker build -t photo_lab_image .
docker run -p 8050:8050 -it --rm --name photo_lab photo_lab_image
echo Deleting docker container
pause

