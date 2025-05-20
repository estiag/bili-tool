@echo off

echo "start build..."

:confirm
set /p choice="This action will clear folder[./download, ./build, ./dist, ./config/user.conf] do you want to continue? [y/n] "
if /i "%choice%"=="y" goto yes
if /i "%choice%"=="n" goto no
echo "Please input y or n"
goto confirm

:yes
rd /s /q ".\download"
rd /s /q ".\build"
rd /s /q ".\dist"
del ".\config\user.conf"

mkdir download
pyi-makespec --add-data "config/*.conf:config" --add-data "static:static" --add-data "templates:templates" --add-data "download:download" --add-data "ffmpeg:ffmpeg" --icon=static/favicon.ico --windowed bilitool.py
pyinstaller bilitool.spec

:no
pause
