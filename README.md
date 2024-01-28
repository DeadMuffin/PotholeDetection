# Pothole Detection System

## Overview

This Python script was implemented during the IP Pothole Detection at FH-Aachen.

It implements a pothole detection system using computer vision and YOLOv8.
The system captures video frames from a camera,
detects potholes in the frames,
then activates a script which captures a picture with a TOF camera
and stores relevant information such as GPS coordinates
and pothole characteristics.

## Features

- Real-time pothole detection using YOLOv8
- Retrieves pothole characteristics like max-depth from TOF camera
- GPS coordinates retrieval
- Optional modes like nogps, notof or headless for non-visual execution
- Capture and storage of pothole images and data

## Prerequisites

Make sure you have Git installed on your system. Download the git repository by running:
```bash 
git clone https://github.com/DeadMuffin/PotholeDetection.git
```

Make sure you have Python 3.9 and 3.7 installed on your system.
To use tof and pothole detection you need two virtuell environments.
When you have successfully installed both venv start the venv with Python3.9 by running:

on mac
```bash
source .yourVenvName/bin/activate
```
on windows
```bash
.\yourVenvName\Scripts\activate
```

Install the required Python3.9 packages by running:
```bash
pip3 install -r requirements.txt
```

For fulfilling the requirements for venv37 take a look in README_TOF.md

## Usage

```bash
python main.py [--headless] [--nogps] [--notof] [--gps_node GPS_NODE] [--weights_path WEIGHTS_PATH] [--cam_source CAM_SOURCE] [--cam_width CAM_WIDTH] [--cam_height CAM_HEIGHT]
```

## Options
- --headless*: Run without video (default: False)
- --nogps*: Run without gps (default: False)
- --notof*: Run without tof (default: False)
- --gps_node : The gps node where the USB is connected. (Defaults to /dev/tty.usbmodem1301").
- --weights_path : Path to the YOLOv8 weights file (default:data models/fallback_best.pt).
- --cam_source : Camera source number (default: 0).
- --cam_width: Camera frame width (default: 1920).
- --cam_height: Camera frame height (default: 1080).

Press Esc or ctr-c in headless to stop the program.

## Results
Detected potholes are stored in the data/results' directory, including
images and corresponding data.

## License
not decided yet