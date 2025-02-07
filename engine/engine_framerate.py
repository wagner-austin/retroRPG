# FileName: engine_framerate.py
# version: 1.0
# Summary: Manages timing and frame delays to maintain a target FPS.
# Tags: engine, performance, timing

import time

def manage_framerate(desired_fps=20):
    """
    Simple fixed-FPS approach using time.sleep().
    For more advanced timing, store 'last_time' and measure dt.
    """
    frame_time = 1.0 / desired_fps
    time.sleep(frame_time)