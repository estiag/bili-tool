#!/bin/bash

echo "start build..."

while true; do
    read -p "This action will clear folder[./download, ./build, ./dist, ./config/user.conf] do you want to continue? [y/n] " choice
    case "$choice" in
        y|Y )
            echo "Cleaning directories..."
            rm -rf ./download ./build ./dist
            rm ./config/user.conf
            rm -r ./ffmpeg/windows
            rm -r ./ffmpeg/mac
            sed -i "s#^ffmpeg_path =.*#ffmpeg_path = ffmpeg/linux/ffmpeg#" ./config/system.conf
            chmod +x ffmpeg/linux/ffmpeg
            mkdir download
            pyi-makespec --add-data "config/*.conf:config" --add-data "static:static" --add-data "templates:templates" --add-data "download:download" --add-data "ffmpeg:ffmpeg" --icon=static/favicon.ico --windowed bilitool.py
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