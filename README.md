# Summary
**vol_control.py** and **vol_overlay.py** are simply programs designed to be run behind the scenes to intercept the media keys (Vol up/down and mute) and control the master Alsa volume level

## vol_control.py
Basic keyboard controls and volume control

## vol_overlay.py
Same as **vol_control.py** but with an added volume bar overlay

# Dependencies
The following dependencies are required for **vol_control.py**

`sudo install python-alsaaudio`

`sudo pip install keyboard`

If you want to run **vol_overlay.py** the following additional dependencies are also required

`sudo apt-get install python-opengl`

# Settings
There is some basic configuration at the top of **vol_overlay.py** if you wish to tweak the behavior or the looks

Setting             | Behavior
--                  | --
OMX_LAYER           | Layer to render overlay
HIDE_DELAY          | Number of seconds to show overlay for after changing volume
BACKGROUND_COLOR    | Color of background image
BACKGROUNDBAR_COLOR | Colour of inactive volume bar
BAR_COLOR           | Color of active volume bar

Additionally, the following images are used and can be changed as required. All images must be saved as 32-bit pngs
Image               | Usage
--                  | --
background.png      | Background shading
bar.png             | Active and inactive volume bar shading
speaker.png         | Unmuted image
muted.png           | Muted image

# Running
Due to globally monitor keyboard input without X11, both *vol_control* and *vol_overlay* must be run as root (See https://pypi.python.org/pypi/keyboard/ for more details)

`sudo python vol_control.py`

or

`sudo python vol_overlay.py`

# Images
Icons from http://www.softicons.com/system-icons/crystal-project-icons-by-everaldo-coelho