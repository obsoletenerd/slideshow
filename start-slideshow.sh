#!/bin/bash
export DISPLAY=:0

# Wait for USB to mount
sleep 3

# Find the USB stick (assumes only one USB storage device)
#PHOTO_PATH=$(find /media/pi -maxdepth 1 -type d | tail -n 1)
PHOTO_PATH="/home/slideshow/photos"

# Path to your logo
LOGO_PATH="/home/slideshow/slideshow/bhack.png"

# Run the slideshow with uv
uv run --with pygame slideshow.py "$USB_PATH" "$PHOTO_PATH"
