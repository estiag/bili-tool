#!/bin/bash

echo "start build..."
if [ -f "venv/bin/activate" ]; then
  source "venv/bin/activate"
fi
while true; do
    read -p "This action will clear folder[download, log, config/user.conf] do you want to continue? [y/n] " choice
    case "$choice" in
        y|Y )
            echo "Cleaning directories..."
            if [ -d "./download" ]; then
              rm -rf ./download
            else
              mkdir download
            fi
            if [ -d "./log" ]; then
              rm -rf ./log
            fi
            if [ -f "./config/user.conf" ]; then
              rm ./config/user.conf
            fi
            sed -i "s#^ffmpeg_path =.*#ffmpeg_path = ffmpeg/linux/ffmpeg#" ./config/system.conf
            chmod +x ffmpeg/linux/ffmpeg

            python -m nuitka --standalone --windows-console-mode=disable \
            --include-data-dir=config=config \
            --include-data-dir=static=static \
            --include-data-dir=templates=templates \
            --include-data-dir=download=download \
            --include-data-files=./ffmpeg/linux/ffmpeg=ffmpeg/linux/ffmpeg \
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