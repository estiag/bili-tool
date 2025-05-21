@echo off

echo "start build..."

:confirm
set /p choice="This action will clear folder[download, log, config/user.conf] do you want to continue? [y/n] "
if /i "%choice%"=="y" goto yes
if /i "%choice%"=="n" goto no
echo "Please input y or n"
goto confirm

:yes
rd /s /q ".\download"
rd /s /q ".\log"
rd /s /q ".\ffmpeg\linux"
rd /s /q ".\ffmpeg\mac"
del ".\config\user.conf"

mkdir download

python -m nuitka --standalone ^
            --macos-create-app-bundle ^
            --include-data-dir=config=config ^
            --include-data-dir=static=static ^
            --include-data-dir=templates=templates ^
            --include-data-dir=download=download ^
            --include-data-dir=ffmpeg=ffmpeg ^
            --macos-app-icon=static/favicon.icon ^
            bilitool.py

:no
pause
