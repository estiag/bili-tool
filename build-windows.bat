@echo off

echo "start build..."

:confirm
set /p choice="This action will clear folder[download, log, config/user.conf] do you want to continue? [y/n] "
if /i "%choice%"=="y" goto yes
if /i "%choice%"=="n" goto no
echo "Please input y or n"
goto confirm

:yes
IF EXIST ".\download" (
    rd /s /q ".\download"
)
IF EXIST ".\log" (
    rd /s /q ".\log"
)
IF EXIST ".\config\user.conf" (
    del ".\config\user.conf"
)
mkdir download

python -m nuitka --standalone --windows-console-mode=disable ^
            --include-data-dir=config=config ^
            --include-data-dir=static=static ^
            --include-data-dir=templates=templates ^
            --include-data-dir=download=download ^
            --include-data-files=./ffmpeg/windows/ffmpeg.exe=ffmpeg/windows/ffmpeg.exe ^
            --windows-icon-from-ico=static/favicon.png ^
            bilitool.py

:no
pause
