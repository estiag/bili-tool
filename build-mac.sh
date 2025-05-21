#!/bin/bash

echo "start build..."

while true; do
    read -p "This action will clear folder[download, build, log, dist, config/user.conf] do you want to continue? [y/n] " choice
    case "$choice" in
        y|Y )
            echo "Cleaning directories..."
            rm -rf ./download ./build ./dist ./log
            rm ./config/user.conf
            rm -r ./ffmpeg/windows
            rm -r ./ffmpeg/linux
            rm -r ./bilitool.build
            rm -r ./bilitool.dist
            sed -i '' "s#^ffmpeg_path =.*#ffmpeg_path = ffmpeg/mac/ffmpeg#" ./config/system.conf
            chmod +x ffmpeg/mac/ffmpeg
            mkdir download

            python -m nuitka --standalone \
            --macos-create-app-bundle \
            --include-data-dir=config=config \
            --include-data-dir=static=static \
            --include-data-dir=templates=templates \
            --include-data-dir=download=download \
            --include-data-dir=ffmpeg=ffmpeg \
            --macos-app-icon=static/favicon.icns \
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