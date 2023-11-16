# RoboPaint

RoboPaint is an application that allows the user to manipulate an industrial robot with their drawings in real time.

![Main window](docs/MainWindow.gif)

## Requirements

* Python >=3.10
* pygame

## Installation

Ubuntu 22.04

```bash
git clone https://github.com/MarcinNarozny/RoboPaint.git
cd RoboPaint
python3 -m pip install -r requirements.txt
```

## Usage

* Check IP addresses of both robot controller and network card of the PC running the app. Port used by the app can be changed in the config.txt file. Location of the robots port may vary depending on the manufacturer.

To start the main app window use:

```bash
cd RoboPaint
python3 -m app
```

You will be welcomed by a pop-up window indicating current connection status. If everything is configured properly main app window will open.
Besides the drawing board there are also special controls palced on the right side of the window:

* Buttons:
    * Test - draws a rectangle on the real drawing surface indicating borders of the maximum drawing space. Useful when setting up robots base. 
    * Move - moves robot away from drawing surface. This buttons functionality is also triggered when closing app window.
    * Clear - erases apps canvas.
* Slider - allows live fine-tuning of the robots drawing tip Z axis. Useful when real drawing surface is not perfectly flat or when drawing tip needs a little more pressure to draw more visibly.

## Authors

* Marcin Narożny ([MarcinNarozny](https://github.com/MarcinNarozny))
* Maciej Nowicki ([mnowicki19](https://github.com/mnowicki19))