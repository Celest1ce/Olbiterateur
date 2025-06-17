# Olbiterateur

Olbiterateur is a small demo that uses a webcam and the [MediaPipe](https://github.com/google/mediapipe) library to detect when you hold up a middle finger. Holding the gesture for a few seconds triggers a system shutdown. The window automatically scales to fit your screen while maintaining the camera aspect ratio.

## Setup

1. Install Python 3.8+.
2. Install dependencies:
   ```bash
   pip install opencv-python mediapipe numpy
   ```
3. Ensure your user has permission to run shutdown commands (Linux may require `sudo`).

## Running

Launch the program with:
```bash
python non.py
```
Press `q` to exit at any time. The window can be resized and will scale the video feed accordingly. If no webcam is found, the program displays an error message and exits when you press `q`.

### Canceling Shutdown
If the gesture was detected by mistake, you can cancel the system shutdown using your OS's normal cancellation command (e.g. `shutdown -c` on Linux). When testing, consider unplugging your computer or using a virtual machine to avoid accidental shutdowns.

## How Fullscreen Scaling Works
The function `resize_with_aspect_ratio` computes the scaling factor based on the target window size and adds padding so the webcam image keeps its aspect ratio. This allows the window to go fullscreen without stretching the camera image.

## Safety Warnings
- The script issues an immediate shutdown command when the gesture is held for the required duration.
- Running it without proper precautions may close applications and lead to data loss.
- Test on a virtual machine or non‑critical system first.

## Architecture
```text
[Webcam] -> [MediaPipe Hand Detection] -> [Gesture Logic] -> [OS Shutdown]
```

### Detection Feedback (ASCII view)
```text
+----------------------------------+
|   middle finger detected  [*]    |
|           MAJEUR DETECTÉ!        |
+----------------------------------+
```


