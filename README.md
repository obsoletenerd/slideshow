# Slideshow

Pygame-based photo slideshow/screensaver.

Created for a specific purpose, probably doesn't suit your needs but it suits mine.

- Configurable countdown timer until next photo
- Countdown bar showing how long until next photo
- Bouncing DVD-screensaver style logo for branding
- Configurable photo source path so it can load photos from a USB stick

## Installing on a fresh Raspberry Pi

Use the Raspberry Pi Imager to put "Raspberry Pi OS Lite (64-bit)" (or the full OS if you want the desktop too) onto a MicroSD card, set up WiFi/SSH/etc.

SSH into the Pi.

Install git:
`sudo apt-get install git`

Install uv:
`curl -LsSf https://astral.sh/uv/install.sh | sh`

Clone this repo to the Pi:
`git clone https://github.com/obsoletenerd/slideshow.git`

Make a directory in the home folder for the photos:
`mkdir photos`

Make the scripts executable:
`chmod +x /home/pi/start_slideshow.sh`
`chmod +x /home/pi/slideshow.py`

Test the `start-slideshow` script:
`./start-slideshow.sh`

Create an autostart file:
`mkdir -p ~/.config/lxsession/LXDE-pi`
`nano ~/.config/lxsession/LXDE-pi/autostart`

Add this line:
`@/home/slideshow/slideshow/start_slideshow.sh`

Reboot.
