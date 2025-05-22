#!/bin/bash

echo "start build..."

while true; do
    read -p "This action will clear folder[download, log, config/user.conf] do you want to continue? [y/n] " choice
    case "$choice" in
        y|Y )
            echo "Cleaning directories..."
            rm -rf ./download ./log
            rm ./config/user.conf
            sed -i "s#^ffmpeg_path =.*#ffmpeg_path = ffmpeg/linux/ffmpeg#" ./config/system.conf
            chmod +x ffmpeg/linux/ffmpeg
            mkdir download

            python -m nuitka --standalone --windows-console-mode=disable \
            --include-data-dir=config=config \
            --include-data-dir=static=static \
            --include-data-dir=templates=templates \
            --include-data-dir=download=download \
            --include-data-files=./ffmpeg/linux/ffmpeg=ffmpeg/linux/ffmpeg \
            --windows-icon-from-ico=./static/favicon.ico \
            bilitool.py

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