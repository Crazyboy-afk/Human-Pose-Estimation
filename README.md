Human Pose Estimation

使用 YOLO Pose 進行人體骨架偵測，目前支援圖片及攝影機即時偵測。

Environment

Python 3.11

Ultralytics YOLO

OpenCV

Installation

Clone or download this repository.

Create a Python virtual environment:

py -3.11 -m venv .venv

Install dependencies:

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Usage

Run the program:

.\.venv\Scripts\python.exe pose.py

The pretrained YOLO Pose model will be downloaded automatically on the first run.