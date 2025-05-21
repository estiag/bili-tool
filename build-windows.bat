@echo off

echo "start build..."

:confirm
set /p choice="This action will clear folder[download, build, log, dist, config/user.conf] do you want to continue? [y/n] "
if /i "%choice%"=="y" goto yes
if /i "%choice%"=="n" goto no
echo "Please input y or n"
goto confirm

:yes
rd /s /q ".\download"
rd /s /q ".\build"
rd /s /q ".\dist"
rd /s /q ".\log"
rd /s /q ".\ffmpeg\linux"
rd /s /q ".\ffmpeg\mac"
rd /s /q ".\bilitool.build"
rd /s /q ".\bilitool.dist"
del ".\config\user.conf"

mkdir download

python -m nuitka --standalone ^
            --macos-create-app-bundle ^
            --include-data-dir=config=config ^
            --include-data-dir=static=static ^
            --include-data-dir=templates=templates ^
            --include-data-dir=download=download ^
            --include-data-dir=ffmpeg=ffmpeg ^
            --macos-app-icon=static/favicon.icns ^
            bilitool.py

:no
pause
