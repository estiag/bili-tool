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
            fi
            if [ -d "./log" ]; then
              rm -rf ./log
            fi
            if [ -f "./config/user.conf" ]; then
              rm ./config/user.conf
            fi
            mkdir download
            sed -i "s#^ffmpeg_path =.*#ffmpeg_path = ffmpeg/linux/ffmpeg#" ./config/system.conf
            chmod +x ffmpeg/linux/ffmpeg

            pyi-makespec \
              --add-data "config/*.conf:config" \
              --add-data "static:static" \
              --add-data "templates:templates" \
              --add-data "download:download" \
              --add-data "ffmpeg:ffmpeg" \
              --icon=static/favicon.ico \
              --windowed bilitool.py

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