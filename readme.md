This repository contains all of the code used to **transmit, receive, and decode information** using the RGB keyboard side-channel attack described in my Master's Report. The code to generate figures for the report is also included. 

## 📁 Contents
- `m1_transmitting/`: Code for data transmission via keyboard RGB LEDs
- `m2_video_processing/`: Splitting the video and determining key colours in each frame
- `m3_colour_correction/`: Training the colour correction models
- `m4_demodulation_and_decoding/`: Demodulating and decoding data from the colour vs time carrier signal
- `m5_figure_generating/`: Scripts for generating figures for the report
- `common/`: Shared utilities

## 🛠 Requirements

Install dependencies using:

```bash
pip install -r requirements.txt