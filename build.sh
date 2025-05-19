#!/bin/bash

echo "start build..."

while true; do
    read -p "This action will clear folder[./download, ./build, ./dist, ./config/user.conf, ./ffmpeg/ffmpeg.exe] do you want to continue? [y/n] " choice
    case "$choice" in
        y|Y )
            echo "Cleaning directories..."
            rm -rf ./download ./build ./dist
            rm ./config/user.conf
            rm ./ffmpeg/ffmpeg.exe
            mkdir download
            pyi-makespec --add-data "config/*.conf:config" --add-data "static:static" --add-data "templates:templates" --add-data "download:download" --icon=static/favicon.ico --windowed bilitool.py
            pyinstaller bilitool.spec
            break
            ;;
        n|N )
            echo "Operation cancelled."
            read -p "Press [Enter] to continue..."
            exit 0
            ;;
        * )
            echo "Please input y or n"
            ;;
    esac
done